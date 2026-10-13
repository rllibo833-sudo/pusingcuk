"""Tests for the shared syntax/runtime diagnostic contract and manifest schema."""
import unittest

from tools.conformance import (
    classify_stderr,
    load_manifest,
    source_line_from_stderr,
)


class ConformanceContractTests(unittest.TestCase):
    def test_diagnostic_classes_are_stable_and_host_language_neutral(self):
        self.assertIsNone(classify_stderr(0, ""))
        self.assertEqual(
            classify_stderr(2, "Kesalahan sintaks: Baris 2, kolom 8: ekspresi tidak valid\n"),
            "syntax_error",
        )
        self.assertEqual(
            classify_stderr(2, "Kesalahan sintaks: Baris 2: ekspresi tidak valid\n"),
            "syntax_error",
        )
        self.assertEqual(
            classify_stderr(1, "Kesalahan runtime: Baris 7: variabel belum dibuat\n"),
            "runtime_error",
        )
        self.assertEqual(classify_stderr(1, "panic: internal error\n"), "error")
        self.assertEqual(source_line_from_stderr("Kesalahan sintaks: Baris 12, kolom 4: salah\n"), 12)
        self.assertEqual(source_line_from_stderr("Kesalahan runtime: baris 3: salah\n"), 3)
        self.assertIsNone(source_line_from_stderr("error tanpa lokasi\n"))

    def test_manifest_uses_one_exit_code_contract_for_all_runtimes(self):
        fixtures = load_manifest()
        self.assertTrue(fixtures)
        for item, path in fixtures:
            expected = item["expected"]
            self.assertNotIn("exit_code_by_runtime", expected, item["id"])
            if expected["stderr_class"] == "syntax_error":
                self.assertEqual(expected["exit_code"], 2, item["id"])
            elif expected["stderr_class"] == "runtime_error":
                self.assertEqual(expected["exit_code"], 1, item["id"])
                self.assertGreaterEqual(expected["source_line"], 1, item["id"])
            else:
                self.assertEqual(expected["exit_code"], 0, item["id"])
                self.assertNotIn("source_line", expected, item["id"])
            if path.suffix == ".cuk":
                self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
