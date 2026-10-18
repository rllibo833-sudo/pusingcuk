"""Regression tests for the generic, bounded .cuk diagnostic helper."""
import tempfile
import unittest
from pathlib import Path

from tools import diagnostic_repair_loop as diag

ROOT = Path(__file__).resolve().parents[1]


class DiagnosticRepairLoopTests(unittest.TestCase):
    def test_valid_source_runs_and_records_hash(self):
        result = diag.run_case(ROOT / "halo.cuk")
        self.assertEqual(result["status"], "passed", result)
        self.assertEqual(result["code"], "OK")
        self.assertEqual(len(result["source_sha256"]), 64)

    def test_wrong_expected_output_is_manual_only(self):
        result = diag.run_case(ROOT / "halo.cuk", ["this-is-not-the-output"])
        self.assertEqual(result["code"], "OUTPUT_MISMATCH")
        self.assertFalse(result["repair"]["automatic_apply"])
        self.assertEqual(result["ai_handoff"]["mode"], "proposal_only")

    def test_non_cuk_source_is_rejected(self):
        result = diag.run_case(ROOT / "README.md")
        self.assertEqual(result["code"], "SOURCE_NOT_CUK")

    def test_outside_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            result = diag.run_case(Path(directory) / "x.cuk")
        self.assertEqual(result["code"], "SOURCE_OUTSIDE_REPOSITORY")


if __name__ == "__main__":
    unittest.main()
