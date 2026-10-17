import unittest
from pathlib import Path

from tools.cuk_coder import build_program, check_source, extract_source


VALID = "jancuk\nlah angka = 40\nhedeh angka + 2\nselesai jancuk\n"


class FakeProvider:
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def generate(self, messages, *, system_prompt=None):
        self.calls.append((messages, system_prompt))
        if not self.answers:
            raise AssertionError("unexpected model call")
        return self.answers.pop(0)


class CukCoderTests(unittest.TestCase):
    def test_extracts_only_one_cuk_block(self):
        self.assertEqual(extract_source("Program:\n\n```cuk\n" + VALID + "```"), VALID)
        with self.assertRaisesRegex(ValueError, "AMBIGUOUS"):
            extract_source("```cuk\na\n```\n```cuk\nb\n```")

    def test_repair_uses_compiler_diagnostic_and_stops_on_pass(self):
        provider = FakeProvider([
            "```cuk\nsource salah\n```",
            "```cuk\n" + VALID + "```",
        ])
        checks = iter([
            {"ok": False, "diagnostic": "Baris 2, kolom 1: expected lah"},
            {"ok": True, "diagnostic": ""},
        ])
        result = build_program(provider, "buat contoh hitung 40 + 2", checker=lambda source: next(checks))
        self.assertEqual(result["status"], "compile_passed")
        self.assertEqual(result["repairs"], 1)
        self.assertEqual(result["source"], VALID)
        self.assertIn("expected lah", provider.calls[1][0][-1]["content"])
        self.assertFalse(result["runtime_tested"])

    def test_repair_limit_is_bounded(self):
        provider = FakeProvider(["```cuk\ninvalid\n```"] * 3)
        result = build_program(provider, "buat contoh", max_repairs=2,
                               checker=lambda source: {"ok": False, "diagnostic": "syntax"})
        self.assertEqual(result["status"], "compile_failed")
        self.assertEqual(len(result["attempts"]), 3)
        self.assertEqual(len(provider.calls), 3)

    def test_rejects_invalid_request_and_repair_limit(self):
        provider = FakeProvider([])
        with self.assertRaisesRegex(ValueError, "REQUEST_INVALID"):
            build_program(provider, " ")
        with self.assertRaisesRegex(ValueError, "REPAIR_LIMIT_INVALID"):
            build_program(provider, "buat contoh", max_repairs=4)

    def test_real_compiler_accepts_minimal_program(self):
        result = check_source(VALID)
        self.assertTrue(result["ok"], result["diagnostic"])


if __name__ == "__main__":
    unittest.main()
