"""Regression tests for the independent PusingCuk knowledge-grounding contract."""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from library.knowledge_grounding import (
    KnowledgeIndexError, append_citations, format_citations, load_index, rank_knowledge,
    validate_index, validate_source,
)

COMMIT = "0123456789abcdef0123456789abcdef01234567"


def source(index: int, title: str, *, path: str | None = None, keywords=None, summary=""):
    source_path = path or f"docs/primer-{index}.md"
    return {
        "id": f"primer-{index}", "title": title, "path": source_path,
        "url": f"https://github.com/example/project/blob/{COMMIT}/{source_path}",
        "source_repository": "example/project", "source_commit": COMMIT,
        "authority": "PRIMARY", "evidence_type": "contract",
        "claim_status": "documented", "visibility": "public-safe",
        "topics": ["pusingcuk", "bahasa indonesia"],
        "keywords": keywords or [], "summary": summary, "excerpt": "",
    }


class KnowledgeGroundingTests(unittest.TestCase):
    def setUp(self):
        titles = [
            "Runtime bahasa PusingCuk", "Kontrak parser dan lexer", "Keamanan eksekusi aturan",
            "Memori percakapan", "Pencarian pengetahuan Indonesia", "Validasi sitasi sumber",
            "Adapter model lokal Ollama", "Batas pemanggilan tool", "Pengujian regresi AI",
            "Provenance commit GitHub", "Indeks dokumen primer", "Kebijakan privasi data",
            "Penanganan timeout provider", "Evaluasi relevansi retrieval",
        ]
        self.documents = [source(i + 1, title, keywords=[title.lower()], summary=title.lower())
                          for i, title in enumerate(titles)]

    def test_all_fourteen_curated_sources_validate(self):
        index = {"schema_version": "pusingcuk.knowledge-index.v1", "documents": self.documents}
        self.assertEqual(len(validate_index(index)), 14)

    def test_real_curated_index_contains_fourteen_pinned_sources(self):
        index_path = Path(__file__).resolve().parents[1] / "library" / "knowledge_index.json"
        documents = load_index(index_path)
        self.assertEqual(len(documents), 14)
        self.assertEqual(len({doc["id"] for doc in documents}), 14)

    def test_real_index_indonesian_query_finds_local_first_decision(self):
        index_path = Path(__file__).resolve().parents[1] / "library" / "knowledge_index.json"
        documents = load_index(index_path)
        results = rank_knowledge(documents, "model lokal ollama tanpa biaya api", limit=3)
        self.assertTrue(results)
        self.assertEqual(results[0]["id"], "local-first-ai-decision")
        self.assertEqual(results[0]["source_commit"], "38ad3035af7e7eaba8a332656ab6155dcc313c72")
        self.assertEqual(results[0]["source_path"], "docs/LOCAL_FIRST_PUSINGCUK_AI.md")

    def test_indonesian_query_ranks_relevant_title_first(self):
        results = rank_knowledge(self.documents, "bagaimana validasi sitasi sumber", limit=3)
        self.assertTrue(results)
        self.assertEqual(results[0]["id"], "primer-6")
        self.assertIn("sitasi", results[0]["matched_terms"])

    def test_accent_and_case_normalisation_is_stable(self):
        doc = source(99, "Evaluasi relevansi retrieval", keywords=["relevansi"])
        self.assertEqual(rank_knowledge([doc], "EVALUASI RELEVANSI", 1)[0]["id"], "primer-99")

    def test_unrelated_query_returns_no_false_positive(self):
        self.assertEqual(rank_knowledge(self.documents, "zebra xylophone nebula", 3), [])

    def test_source_commit_must_match_url_commit(self):
        bad = copy.deepcopy(self.documents[0])
        bad["source_commit"] = "f" * 40
        self.assertFalse(validate_source(bad))

    def test_source_path_must_match_url_path(self):
        bad = copy.deepcopy(self.documents[0])
        bad["path"] = "docs/other.md"
        self.assertFalse(validate_source(bad))

    def test_rejects_non_github_and_query_urls(self):
        for url in ("https://evil.example/x", self.documents[0]["url"] + "?raw=1"):
            bad = copy.deepcopy(self.documents[0])
            bad["url"] = url
            with self.subTest(url=url):
                self.assertFalse(validate_source(bad))

    def test_rejects_non_public_safe_documents(self):
        bad = copy.deepcopy(self.documents[0])
        bad["visibility"] = "private"
        with self.assertRaises(KnowledgeIndexError):
            validate_index({"schema_version": "pusingcuk.knowledge-index.v1", "documents": [bad]})

    def test_rejects_duplicate_ids(self):
        with self.assertRaisesRegex(KnowledgeIndexError, "DUPLICATE_ID"):
            validate_index({"schema_version": "pusingcuk.knowledge-index.v1", "documents": [self.documents[0], self.documents[0]]})

    def test_rejects_oversized_index(self):
        with self.assertRaisesRegex(KnowledgeIndexError, "SIZE_INVALID"):
            validate_index({"schema_version": "pusingcuk.knowledge-index.v1", "documents": self.documents * 8})

    def test_citations_use_only_validated_sources_and_are_deduplicated(self):
        bad = copy.deepcopy(self.documents[0])
        bad["url"] = "https://attacker.example/fake"
        output = format_citations([self.documents[0], self.documents[0], bad])
        self.assertEqual(output.count(self.documents[0]["url"]), 1)
        self.assertNotIn("attacker.example", output)

    def test_answer_citations_are_not_inferred_from_model_text(self):
        answer = append_citations("Jawaban dengan tautan palsu https://attacker.example", [self.documents[1]])
        self.assertIn(self.documents[1]["url"], answer)
        self.assertNotIn("[https://attacker.example]", answer)

    def test_empty_answer_stays_empty(self):
        self.assertEqual(append_citations("  ", self.documents), "")

    def test_invalid_query_and_limit_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "QUERY_INVALID"):
            rank_knowledge(self.documents, "   ")
        with self.assertRaisesRegex(ValueError, "LIMIT_INVALID"):
            rank_knowledge(self.documents, "memori", 6)

    def test_result_count_is_bounded(self):
        self.assertLessEqual(len(rank_knowledge(self.documents, "pusingcuk", 2)), 2)


if __name__ == "__main__":
    unittest.main()
