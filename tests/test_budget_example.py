"""Tes bahwa contoh anggaran Pusingcuk benar-benar dapat dijalankan oleh CLI."""
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"
EXAMPLE = ROOT / "examples" / "rekap_anggaran.pusingcuk"


class BudgetExampleTests(unittest.TestCase):
    def test_budget_example_runs_and_prints_expected_totals(self):
        result = subprocess.run(
            [sys.executable, str(CLI), str(EXAMPLE)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "REKAP ANGGARAN BULANAN\n"
            "Pendapatan (rupiah):\n"
            "2500000\n"
            "Pengeluaran (rupiah):\n"
            "1200000\n"
            "Sisa (rupiah):\n"
            "1300000\n"
            "Status: anggaran tidak defisit\n",
        )
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
