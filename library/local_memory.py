"""Explicitly user-controlled local project memory for PusingCuk AI."""
from __future__ import annotations

import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from library.knowledge_grounding import tokenize

_SCHEMA = "pusingcuk.local-memory.v1"
_CATEGORIES = {"decision", "constraint", "project_fact", "recovery"}
_MAX_RECORDS = 200
_MAX_TEXT = 2_000
_MAX_FILE_BYTES = 1_000_000
_SECRET_PATTERNS = [
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AIza[A-Za-z0-9_-]{30,})\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}", re.IGNORECASE),
    re.compile(r"\b(?:password|passwd|api[_ -]?key|service[_ -]?role[_ -]?key|secret)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


class LocalMemoryError(ValueError):
    """Stable local-memory validation or I/O error."""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)


class LocalMemoryStore:
    """Persistent project notes; no conversation is saved automatically."""

    def __init__(self, path: str | Path | None = None):
        configured = os.environ.get("PUSINGCUK_AI_MEMORY_PATH")
        self.path = Path(path or configured or (Path.home() / ".pusingcuk" / "memory.json"))

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            if self.path.stat().st_size > _MAX_FILE_BYTES:
                raise LocalMemoryError("MEMORY_FILE_TOO_LARGE")
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except LocalMemoryError:
            raise
        except (OSError, UnicodeError, json.JSONDecodeError):
            raise LocalMemoryError("MEMORY_READ_FAILED") from None
        if not isinstance(payload, dict) or payload.get("schema_version") != _SCHEMA:
            raise LocalMemoryError("MEMORY_SCHEMA_INVALID")
        records = payload.get("records")
        if not isinstance(records, list) or len(records) > _MAX_RECORDS:
            raise LocalMemoryError("MEMORY_RECORDS_INVALID")
        seen = set()
        for record in records:
            if not isinstance(record, dict) or set(record) != {"id", "category", "text", "created_at"}:
                raise LocalMemoryError("MEMORY_RECORD_INVALID")
            if not isinstance(record["id"], str) or not record["id"] or record["id"] in seen:
                raise LocalMemoryError("MEMORY_RECORD_ID_INVALID")
            if (
                not isinstance(record["category"], str)
                or record["category"] not in _CATEGORIES
                or not isinstance(record["text"], str)
                or not record["text"].strip()
                or len(record["text"]) > _MAX_TEXT
            ):
                raise LocalMemoryError("MEMORY_RECORD_CONTENT_INVALID")
            if _contains_secret(record["text"]):
                raise LocalMemoryError("MEMORY_SECRET_DETECTED")
            if not isinstance(record["created_at"], str):
                raise LocalMemoryError("MEMORY_TIMESTAMP_INVALID")
            seen.add(record["id"])
        return records

    def _save(self, records: list[dict[str, Any]]) -> None:
        if len(records) > _MAX_RECORDS:
            raise LocalMemoryError("MEMORY_RECORD_LIMIT_REACHED")
        parent = self.path.parent
        try:
            parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            if os.name == "posix":
                os.chmod(parent, 0o700)
            content = json.dumps({"schema_version": _SCHEMA, "records": records}, ensure_ascii=False, indent=2) + "\n"
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=parent, prefix=".memory-", delete=False) as handle:
                temporary = Path(handle.name)
                if os.name == "posix":
                    os.chmod(temporary, 0o600)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
            if os.name == "posix":
                os.chmod(self.path, 0o600)
        except OSError:
            try:
                temporary.unlink(missing_ok=True)
            except (OSError, UnboundLocalError):
                pass
            raise LocalMemoryError("MEMORY_WRITE_FAILED") from None

    def remember(self, text: str, *, category: str = "decision", confirmed: bool = False) -> dict[str, Any]:
        if confirmed is not True:
            raise LocalMemoryError("MEMORY_CONFIRMATION_REQUIRED")
        if not isinstance(category, str) or category not in _CATEGORIES:
            raise LocalMemoryError("MEMORY_CATEGORY_INVALID")
        if not isinstance(text, str) or not text.strip() or len(text.strip()) > _MAX_TEXT:
            raise LocalMemoryError("MEMORY_TEXT_INVALID")
        clean = " ".join(text.strip().split())
        if _contains_secret(clean):
            raise LocalMemoryError("MEMORY_SECRET_DETECTED")
        records = self._load()
        record = {"id": uuid.uuid4().hex[:12], "category": category, "text": clean, "created_at": _now()}
        records.append(record)
        self._save(records)
        return record.copy()

    def list_records(self, *, limit: int = 20) -> list[dict[str, Any]]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
            raise LocalMemoryError("MEMORY_LIMIT_INVALID")
        return [record.copy() for record in self._load()[::-1][:limit]]

    def search(self, query: str, *, limit: int = 3) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip() or len(query) > 300:
            raise LocalMemoryError("MEMORY_QUERY_INVALID")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10:
            raise LocalMemoryError("MEMORY_LIMIT_INVALID")
        terms = set(tokenize(query))
        if not terms:
            return []
        ranked = []
        for record in self._load():
            matched = sorted(terms.intersection(tokenize(record["text"])))
            if matched:
                ranked.append((len(matched), record["created_at"], record, matched))
        ranked.sort(key=lambda item: (-item[0], item[1], item[2]["id"]))
        return [{**record.copy(), "matched_terms": matched} for _score, _created, record, matched in ranked[:limit]]

    def delete(self, record_id: str, *, confirmed: bool = False) -> bool:
        if confirmed is not True:
            raise LocalMemoryError("MEMORY_CONFIRMATION_REQUIRED")
        if not isinstance(record_id, str) or not record_id.strip():
            raise LocalMemoryError("MEMORY_RECORD_ID_INVALID")
        records = self._load()
        remaining = [record for record in records if record["id"] != record_id]
        if len(remaining) == len(records):
            return False
        self._save(remaining)
        return True
