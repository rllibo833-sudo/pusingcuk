"""Regression tests for pure business rules intended for CORE CI integration."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"
FIXTURE = ROOT / "examples" / "core" / "anggaran_sufficiency.cuk"


class CoreBudgetRuleTests(unittest.TestCase):
    def test_budget_sufficiency_reference_fixture(self):
        result = subprocess.run(
            [sys.executable, str(CLI), str(FIXTURE)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "SALDO_CUKUP\n"
            "SALDO_CUKUP\n"
            "SALDO_TIDAK_CUKUP\n"
            "SALDO_CUKUP\n"
            "INPUT_TIDAK_VALID\n"
            "INPUT_TIDAK_VALID\n",
        )
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
