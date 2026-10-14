"""Tests for explicit, bounded, secret-aware local project memory."""
import json
import tempfile
import unittest
from pathlib import Path

from library.local_memory import LocalMemoryError, LocalMemoryStore


class LocalMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pusingcuk-memory-")
        self.path = Path(self.temp.name) / "private" / "memory.json"
        self.store = LocalMemoryStore(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_memory_requires_explicit_confirmation(self):
        with self.assertRaisesRegex(LocalMemoryError, "CONFIRMATION_REQUIRED"):
            self.store.remember("PusingCuk tetap proyek utama.")

    def test_remember_persists_and_searches_project_decision(self):
        record = self.store.remember("PusingCuk adalah repositori utama; CORE dan Founder OS dibekukan setelah migrasi.", confirmed=True)
        results = self.store.search("repositori utama PusingCuk", limit=3)
        self.assertEqual(results[0]["id"], record["id"])
        self.assertEqual(self.store.list_records()[0]["text"], record["text"])

    def test_secret_like_values_are_rejected(self):
        cases = ["api_key=abc123", "Bearer abcdefghijklmnopqrstuvwxyz012345", "ghp_" + "A" * 30]
        for value in cases:
            with self.subTest(value=value), self.assertRaisesRegex(LocalMemoryError, "SECRET_DETECTED"):
                self.store.remember("Catatan proyek " + value, confirmed=True)

    def test_categories_and_sizes_are_validated(self):
        with self.assertRaisesRegex(LocalMemoryError, "CATEGORY_INVALID"):
            self.store.remember("Keputusan", category="other", confirmed=True)
        with self.assertRaisesRegex(LocalMemoryError, "TEXT_INVALID"):
            self.store.remember("x" * 2_001, confirmed=True)

    def test_delete_requires_confirmation_and_removes_record(self):
        record = self.store.remember("Gunakan model lokal.", confirmed=True)
        with self.assertRaisesRegex(LocalMemoryError, "CONFIRMATION_REQUIRED"):
            self.store.delete(record["id"])
        self.assertTrue(self.store.delete(record["id"], confirmed=True))
        self.assertFalse(self.store.list_records())

    def test_corrupt_schema_fails_closed(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"schema_version": "wrong", "records": []}), encoding="utf-8")
        with self.assertRaisesRegex(LocalMemoryError, "SCHEMA_INVALID"):
            self.store.list_records()

    def test_memory_limit_is_bounded(self):
        with self.assertRaisesRegex(LocalMemoryError, "LIMIT_INVALID"):
            self.store.list_records(limit=1000)
        with self.assertRaisesRegex(LocalMemoryError, "LIMIT_INVALID"):
            self.store.search("decision", limit=11)
        with self.assertRaisesRegex(LocalMemoryError, "QUERY_INVALID"):
            self.store.search(" ")


if __name__ == "__main__":
    unittest.main()
