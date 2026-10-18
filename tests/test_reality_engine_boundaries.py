"""Focused boundary regressions for the Cuk Reality Engine example."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"
EXAMPLE = ROOT / "examples" / "reality_engine.cuk"


class RealityEngineBoundaryTests(unittest.TestCase):
    def run_engine(self, user_input):
        return subprocess.run(
            [sys.executable, str(CLI), str(EXAMPLE)],
            cwd=ROOT,
            input=user_input,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_zero_percent_is_valid_and_uses_low_reserve_rule(self):
        result = self.run_engine("0\nya\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AIR-01: CADANGAN_RENDAH_KEBUTUHAN_DASAR", result.stdout)
        self.assertIn("PRIORITASKAN_KEBUTUHAN_DASAR", result.stdout)

    def test_one_hundred_percent_is_valid_and_uses_normal_rule(self):
        result = self.run_engine("100\ntidak\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AIR-04: KONDISI_NORMAL", result.stdout)
        self.assertIn("KONDISI_NORMAL", result.stdout)

    def test_negative_reserve_is_rejected_before_policy_decision(self):
        result = self.run_engine("-1\nya\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AIR-00: INPUT_CADANGAN_TIDAK_VALID", result.stdout)
        self.assertIn("MASUKAN_TIDAK_VALID", result.stdout)
        self.assertNotIn("PRIORITASKAN_KEBUTUHAN_DASAR", result.stdout)
        self.assertNotIn("KONDISI_NORMAL", result.stdout)

    def test_fraction_above_one_hundred_is_rejected(self):
        result = self.run_engine("100.1\ntidak\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AIR-00: INPUT_CADANGAN_TIDAK_VALID", result.stdout)
        self.assertIn("MASUKAN_TIDAK_VALID", result.stdout)
        self.assertNotIn("KONDISI_NORMAL", result.stdout)


if __name__ == "__main__":
    unittest.main()
