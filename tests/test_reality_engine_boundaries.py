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


    def test_one_rule_result_drives_decision_reason_and_action(self):
        cases = (
            ("15\nya\n", "AIR-01: CADANGAN_RENDAH_KEBUTUHAN_DASAR", "PRIORITASKAN_KEBUTUHAN_DASAR", "kebutuhan dasar diprioritaskan", "Amankan air untuk minum"),
            ("20\ntidak\n", "AIR-02: CADANGAN_RENDAH_BATASI_NON_ESENSIAL", "BATASI_PENGGUNAAN_NON_ESENSIAL", "penggunaan non-esensial dibatasi", "Batasi pemakaian non-esensial"),
            ("21\nya\n", "AIR-03: PENGHEMATAN", "HEMAT_AIR", "terapkan penghematan", "Terapkan penghematan"),
            ("51\ntidak\n", "AIR-04: KONDISI_NORMAL", "KONDISI_NORMAL", "kondisi normal", "Pertahankan pemantauan berkala"),
            ("101\nya\n", "AIR-00: INPUT_CADANGAN_TIDAK_VALID", "MASUKAN_TIDAK_VALID", "cadangan harus 0 sampai 100%", "Periksa ulang data cadangan"),
        )
        for user_input, rule, decision, reason, action in cases:
            with self.subTest(user_input=user_input):
                result = self.run_engine(user_input)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(rule, result.stdout)
                self.assertIn(decision, result.stdout)
                self.assertIn(reason, result.stdout)
                self.assertIn(action, result.stdout)


if __name__ == "__main__":
    unittest.main()
