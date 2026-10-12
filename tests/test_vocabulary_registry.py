"""Consistency checks for the public vocabulary registry."""
import json
import unittest
from pathlib import Path

from lexer import KEYWORD_ALIASES


ROOT = Path(__file__).resolve().parents[1]


class VocabularyRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(
            (ROOT / "library" / "kosakata.json").read_text(encoding="utf-8")
        )
        cls.entries = cls.registry["keywords"]

    def test_registry_has_supported_schema(self):
        self.assertEqual(self.registry["schema_version"], 1)
        self.assertEqual(self.registry["language"], "Pusingcuk")
        self.assertIsInstance(self.entries, list)
        self.assertTrue(self.entries)

    def test_alias_mapping_matches_lexer(self):
        documented = {}
        canonical_words = {entry["word"] for entry in self.entries}

        for entry in self.entries:
            word = entry["word"]
            for alias in entry.get("aliases", []):
                self.assertNotIn(alias, documented, f"Duplicate alias: {alias}")
                documented[alias] = word

            canonical = entry.get("alias_of")
            if canonical:
                self.assertIn(canonical, canonical_words, f"Unknown canonical word for {word}")
                self.assertNotIn(word, documented, f"Duplicate alias: {word}")
                documented[word] = canonical

        self.assertEqual(
            documented,
            KEYWORD_ALIASES,
            "Update library/kosakata.json whenever lexer aliases change, and vice versa.",
        )

    def test_registry_source_documents_exist(self):
        for relative_path in self.registry.get("source_of_truth", []):
            with self.subTest(path=relative_path):
                self.assertTrue(
                    (ROOT / "library" / relative_path).resolve().is_file(),
                    f"Missing vocabulary reference: {relative_path}",
                )


if __name__ == "__main__":
    unittest.main()
