"""Regression tests for the independent PusingCuk knowledge-grounding contract."""
from __future__ import annotations

import copy
import json
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

    def test_real_curated_index_contains_twenty_locally_owned_sources(self):
        index_path = Path(__file__).resolve().parents[1] / "library" / "knowledge_index.json"
        documents = load_index(index_path)
        self.assertEqual(len(documents), 20)
        self.assertEqual(len({doc["id"] for doc in documents}), 20)
        # All runtime retrieval records are locally owned. Each URL must match its
        # exact immutable source commit/path; the index's own citation deliberately
        # points to the earlier 14-record local-only normalization snapshot.
        self.assertEqual({doc["source_repository"] for doc in documents}, {"rllibo833-sudo/pusingcuk"})
        for document in documents:
            self.assertEqual(
                document["url"],
                f"https://github.com/rllibo833-sudo/pusingcuk/blob/{document['source_commit']}/{document['path']}",
            )
        curated_index = next(doc for doc in documents if doc["id"] == "pusingcuk-curated-index")
        self.assertEqual(curated_index["source_commit"], "983304b16f4f41e51e4569bccd34d6c32815a447")
        self.assertIn("pusingcuk-ai-migration-ledger", {doc["id"] for doc in documents})
        self.assertIn("pusingcuk-local-ai-service", {doc["id"] for doc in documents})
        self.assertIn("pusingcuk-kawasan-masterplan-operating-model", {doc["id"] for doc in documents})
        self.assertTrue({"pusingcuk-founder-authority-evidence", "pusingcuk-local-provider-rule-safety", "pusingcuk-core-retirement-manifest"}.issubset({doc["id"] for doc in documents}))

    def test_changed_primary_docs_pin_the_reviewed_snapshot(self):
        index_path = Path(__file__).resolve().parents[1] / "library" / "knowledge_index.json"
        documents = {doc["id"]: doc for doc in load_index(index_path)}
        snapshot = "f035f2e514e0d407baea30f4bdfec4c9fa661a59"
        for doc_id in (
            "pusingcuk-project-overview",
            "pusingcuk-ai-grounding-policy",
            "pusingcuk-ai-migration-ledger",
        ):
            with self.subTest(doc_id=doc_id):
                document = documents[doc_id]
                self.assertEqual(document["source_commit"], snapshot)
                self.assertEqual(
                    document["url"],
                    f"https://github.com/rllibo833-sudo/pusingcuk/blob/{snapshot}/{document['path']}",
                )

    def test_real_index_indonesian_query_finds_local_first_decision(self):
        index_path = Path(__file__).resolve().parents[1] / "library" / "knowledge_index.json"
        documents = load_index(index_path)
        results = rank_knowledge(documents, "model lokal ollama tanpa biaya api", limit=3)
        self.assertTrue(results)
        self.assertEqual(results[0]["id"], "pusingcuk-local-ai-provider")
        self.assertEqual(results[0]["source_commit"], "733d4328a8d4433b1633e8d3bba9601786c2e08a")
        self.assertEqual(results[0]["source_path"], "library/local_ai_provider.py")

    def test_founder_core_transfer_sources_are_pinned_to_pusingcuk_snapshot(self):
        root = Path(__file__).resolve().parents[1]
        documents = {doc["id"]: doc for doc in load_index(root / "library" / "knowledge_index.json")}
        snapshot = "1db8eb5cbd35fd05cec982ff7db90a1ea31b5e11"
        paths = {
            "pusingcuk-founder-authority-evidence": "docs/ai/DECISION_AUTHORITY_AND_EVIDENCE.md",
            "pusingcuk-local-provider-rule-safety": "docs/ai/LOCAL_MODEL_AND_RULE_SAFETY.md",
            "pusingcuk-core-retirement-manifest": "docs/migration/FOUNDER_OS_CORE_RETIREMENT_MANIFEST.md",
        }
        for doc_id, path in paths.items():
            with self.subTest(doc_id=doc_id):
                document = documents[doc_id]
                self.assertEqual(document["source_repository"], "rllibo833-sudo/pusingcuk")
                self.assertEqual(document["source_commit"], snapshot)
                self.assertEqual(document["path"], path)
                self.assertEqual(document["url"], f"https://github.com/rllibo833-sudo/pusingcuk/blob/{snapshot}/{path}")

    def test_conceptual_masterplan_source_is_pinned_to_owned_commit(self):
        root = Path(__file__).resolve().parents[1]
        documents = {doc["id"]: doc for doc in load_index(root / "library" / "knowledge_index.json")}
        document = documents["pusingcuk-kawasan-masterplan-operating-model"]
        self.assertEqual(document["source_repository"], "rllibo833-sudo/pusingcuk")
        self.assertEqual(document["source_commit"], "fb5d9570388ec434ad4cd3cb9e9bc0846aface93")
        self.assertEqual(document["path"], "docs/knowledge/KAWASAN_MASJID_MASTERPLAN_AND_OPERATING_MODEL.md")
        self.assertEqual(document["url"], "https://github.com/rllibo833-sudo/pusingcuk/blob/fb5d9570388ec434ad4cd3cb9e9bc0846aface93/docs/knowledge/KAWASAN_MASJID_MASTERPLAN_AND_OPERATING_MODEL.md")
        self.assertIn("conceptual-masterplan", document["claim_status"])

    def test_common_indonesian_slang_maps_to_canonical_search_terms(self):
        from library.knowledge_grounding import tokenize

        self.assertEqual(
            tokenize("gimana jelasin cara nanganin masalah, ga ngarang"),
            ["bagaimana", "menjelaskan", "cara", "menangani", "masalah", "tidak", "mengarang"],
        )

    def test_common_repository_typos_normalize_for_retrieval(self):
        from library.knowledge_grounding import tokenize

        self.assertEqual(
            tokenize("supabse benchmarck retrival"),
            ["supabase", "benchmark", "retrieval"],
        )

    def test_typo_tolerance_recovers_long_query_terms(self):
        document = source(
            99,
            "Benchmark retrieval bahasa Indonesia",
            keywords=["evaluasi pencarian"],
            summary="uji kualitas pencarian pengetahuan",
        )
        results = rank_knowledge([document], "benchmakr retrievel", limit=1)
        self.assertEqual([item["id"] for item in results], ["primer-99"])
        self.assertEqual(set(results[0]["matched_terms"]), {"benchmarck", "retrival"})

    def test_indonesian_retrieval_benchmark_top_one(self):
        root = Path(__file__).resolve().parents[1]
        documents = load_index(root / "library" / "knowledge_index.json")
        cases = json.loads((root / "tests" / "fixtures" / "knowledge_retrieval_cases.json").read_text(encoding="utf-8"))["cases"]
        self.assertEqual(len(cases), 20)
        correct = 0
        for case in cases:
            with self.subTest(case=case["id"]):
                results = rank_knowledge(documents, case["query"], limit=3)
                self.assertTrue(results, f"no retrieval result for {case['query']}")
                if results[0]["id"] == case["expected_top_id"]:
                    correct += 1
                self.assertEqual(results[0]["id"], case["expected_top_id"])
        self.assertEqual(correct, 20)

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
        self.assertNotIn("attacker.example", answer)

    def test_empty_answer_stays_empty(self):
        self.assertEqual(append_citations("  ", self.documents), "")

    def test_model_markdown_link_destination_is_removed(self):
        answer = append_citations("Buka [tautan](https://attacker.example/path).", [])
        self.assertIn("tautan", answer)
        self.assertNotIn("https://", answer)
        self.assertNotIn("](", answer)

    def test_invalid_query_and_limit_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "QUERY_INVALID"):
            rank_knowledge(self.documents, "   ")
        with self.assertRaisesRegex(ValueError, "LIMIT_INVALID"):
            rank_knowledge(self.documents, "memori", 6)

    def test_result_count_is_bounded(self):
        self.assertLessEqual(len(rank_knowledge(self.documents, "pusingcuk", 2)), 2)


if __name__ == "__main__":
    unittest.main()
