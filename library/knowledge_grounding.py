"""Deterministic, provenance-checked retrieval for PusingCuk AI.

This module intentionally uses only the Python standard library. It ranks a
small, explicitly curated index; it is not vector search and does not treat
retrieved documents as executable instructions.
"""
from __future__ import annotations

import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Iterable

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_TOKEN_RE = re.compile(r"[^\w]+", re.UNICODE)
_REQUIRED = {
    "id", "title", "path", "url", "source_repository", "source_commit",
    "authority", "evidence_type", "claim_status", "visibility",
}
_SEARCH_FIELDS = ("title", "topics", "keywords", "summary", "excerpt")


class KnowledgeIndexError(ValueError):
    """Raised when a curated knowledge index violates its provenance contract."""


def _normalise(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.casefold()


_INDONESIAN_QUERY_ALIASES = {
    # Common conversational Indonesian forms mapped to their canonical forms.
    "gimana": "bagaimana",
    "gmn": "bagaimana",
    "jelasin": "menjelaskan",
    "nanganin": "menangani",
    "ngubungin": "menghubungkan",
    "ngarang": "mengarang",
    "ga": "tidak",
    "gak": "tidak",
    "nggak": "tidak",
    "enggak": "tidak",
    # Frequent typos seen in repository and benchmark queries.
    "supabse": "supabase",
    "benchmarck": "benchmark",
    "retrival": "retrieval",
}


def tokenize(value: Any) -> list[str]:
    """Tokenise Indonesian text, normalise common slang, and keep deterministic output."""
    tokens = [token for token in _TOKEN_RE.split(_normalise(value)) if len(token) >= 2]
    return [_INDONESIAN_QUERY_ALIASES.get(token, token) for token in tokens]


def validate_source(source: Any) -> bool:
    """Validate a public-safe immutable GitHub source envelope."""
    if not isinstance(source, dict) or not _REQUIRED.issubset(source):
        return False
    if source.get("visibility") != "public-safe":
        return False
    if not isinstance(source.get("id"), str) or not source["id"].strip():
        return False
    if not isinstance(source.get("title"), str) or not source["title"].strip():
        return False
    repo = source.get("source_repository")
    commit = source.get("source_commit")
    path = source.get("path")
    url_text = source.get("url")
    if not isinstance(repo, str) or not _REPO_RE.fullmatch(repo):
        return False
    if not isinstance(commit, str) or not _SHA_RE.fullmatch(commit):
        return False
    if (
        not isinstance(path, str)
        or not path
        or path.startswith("/")
        or "\\" in path
        or any(part in {"", ".", ".."} for part in path.split("/"))
        or any(ord(char) < 32 for char in path)
    ):
        return False
    if not isinstance(url_text, str):
        return False
    try:
        url = urlparse(url_text)
    except ValueError:
        return False
    if url.scheme != "https" or url.netloc != "github.com" or url.query or url.fragment:
        return False
    expected_prefix = f"/{repo}/blob/{commit}/"
    if not url.path.startswith(expected_prefix):
        return False
    url_path = url.path[len(expected_prefix):]
    return bool(url_path and url_path == path)


def validate_index(index: Any, *, max_documents: int = 100) -> list[dict[str, Any]]:
    """Validate index envelope and each document; fail closed on any bad entry."""
    if not isinstance(index, dict) or index.get("schema_version") != "pusingcuk.knowledge-index.v1":
        raise KnowledgeIndexError("KNOWLEDGE_INDEX_SCHEMA_INVALID")
    documents = index.get("documents")
    if not isinstance(documents, list) or len(documents) > max_documents:
        raise KnowledgeIndexError("KNOWLEDGE_INDEX_SIZE_INVALID")
    seen: set[str] = set()
    accepted: list[dict[str, Any]] = []
    for position, document in enumerate(documents):
        if not validate_source(document):
            raise KnowledgeIndexError(f"KNOWLEDGE_SOURCE_INVALID:{position}")
        doc_id = document["id"]
        if doc_id in seen:
            raise KnowledgeIndexError(f"KNOWLEDGE_SOURCE_DUPLICATE_ID:{doc_id}")
        seen.add(doc_id)
        for field in ("topics", "keywords"):
            value = document.get(field, [])
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise KnowledgeIndexError(f"KNOWLEDGE_SOURCE_FIELD_INVALID:{doc_id}:{field}")
        for field in ("summary", "excerpt", "authority", "evidence_type", "claim_status"):
            if field in document and not isinstance(document[field], str):
                raise KnowledgeIndexError(f"KNOWLEDGE_SOURCE_FIELD_INVALID:{doc_id}:{field}")
        accepted.append(document)
    return accepted


def load_index(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate a UTF-8 JSON index from an explicit local path."""
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KnowledgeIndexError("KNOWLEDGE_INDEX_READ_FAILED") from exc
    return validate_index(payload)


def rank_knowledge(
    documents: Iterable[dict[str, Any]], query: str, limit: int = 3,
) -> list[dict[str, Any]]:
    """Rank curated sources with deterministic lexical weights and stable ties."""
    if not isinstance(query, str) or not query.strip() or len(query) > 300:
        raise ValueError("KNOWLEDGE_QUERY_INVALID")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 5:
        raise ValueError("KNOWLEDGE_LIMIT_INVALID")
    terms = set(tokenize(query))
    if not terms:
        return []
    phrase = _normalise(query).strip()
    ranked: list[tuple[int, str, dict[str, Any], list[str]]] = []
    for doc in documents:
        if not validate_source(doc):
            continue
        weights = {"title": 6, "topics": 4, "keywords": 3, "summary": 2, "excerpt": 1}
        score = 0
        matched: list[str] = []
        normalised_fields: dict[str, list[str]] = {}
        for field in _SEARCH_FIELDS:
            value = doc.get(field, [])
            normalised_fields[field] = tokenize(" ".join(value) if isinstance(value, list) else value)
        all_field_tokens = set().union(*normalised_fields.values())
        for term in sorted(terms):
            found = False
            for field, weight in weights.items():
                if term in normalised_fields[field]:
                    score += weight
                    found = True
            # Bounded typo tolerance is a fallback only: exact lexical matches
            # always win, and fuzzy matches add just one point rather than
            # inheriting the weight of a title/topic match.
            if not found and len(term) >= 6:
                candidates = (
                    token for token in all_field_tokens
                    if abs(len(token) - len(term)) <= 2
                )
                best = max(
                    candidates,
                    key=lambda token: SequenceMatcher(None, term, token).ratio(),
                    default=None,
                )
                if best is not None and SequenceMatcher(None, term, best).ratio() >= 0.82:
                    score += 1
                    found = True
            if found:
                matched.append(term)
        searchable = _normalise(" ".join(
            " ".join(doc.get(field, [])) if isinstance(doc.get(field, []), list)
            else str(doc.get(field, "")) for field in _SEARCH_FIELDS
        ))
        if len(phrase) >= 4 and phrase in searchable:
            score += 4
        if score and matched:
            ranked.append((score, str(doc["id"]), doc, matched))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    results = []
    for score, _doc_id, doc, matched in ranked[:limit]:
        results.append({
            "id": doc["id"], "title": doc["title"],
            "summary": str(doc.get("summary", ""))[:900],
            "excerpt": str(doc.get("excerpt", ""))[:800],
            "source_path": doc["path"], "source_url": doc["url"],
            "source_repository": doc["source_repository"],
            "source_commit": doc["source_commit"], "authority": doc["authority"],
            "evidence_type": doc["evidence_type"], "claim_status": doc["claim_status"],
            "visibility": doc["visibility"], "score": score, "matched_terms": matched,
        })
    return results


def format_citations(sources: Iterable[dict[str, Any]], limit: int = 5) -> str:
    """Format citations only from validated immutable source records, never model URLs."""
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 5:
        return ""
    lines: list[str] = []
    seen: set[str] = set()
    for source in sources:
        if not validate_source(source):
            continue
        url = source["url"]
        if url in seen:
            continue
        seen.add(url)
        label = re.sub(r"[\r\n\[\]]", " ", source["title"])
        label = " ".join(label.split())[:180] or "Sumber terverifikasi"
        lines.append(f"- [{label}]({url}) — {source['source_repository']} @ {source['source_commit'][:12]}")
        if len(lines) >= limit:
            break
    return "**Sumber rujukan (grounding):**\n" + "\n".join(lines) if lines else ""


def append_citations(answer: str, sources: Iterable[dict[str, Any]]) -> str:
    """Append validated citations and strip URLs emitted by the model."""
    if not isinstance(answer, str) or not answer.strip():
        return ""
    valid_sources = [source for source in sources if validate_source(source)]
    # Model-provided links are untrusted, even when they resemble source URLs.
    # Preserve link labels but remove destinations; trusted links are appended below.
    body = re.sub(r"\[([^\]]+)\]\(https?://[^)\s]+\)", r"\1", answer.strip())
    body = re.sub(r"https?://[^\s<>]+", "", body)
    body = re.sub(r"[ \t]{2,}", " ", body).strip()
    citations = format_citations(valid_sources)
    return f"{body}\n\n{citations}" if citations else body
