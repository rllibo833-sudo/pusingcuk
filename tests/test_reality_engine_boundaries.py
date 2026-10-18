"""Focused boundary regressions for the Cuk Reality Engine example."""

import subprocess
import sys
import tempfile
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

    def test_fractional_reserve_is_rejected_as_invalid_numeric_input(self):
        # Decimal input is parsed first, then rejected by the 0–100 policy boundary.
        result = self.run_engine("100.1\ntidak\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AIR-00: INPUT_CADANGAN_TIDAK_VALID", result.stdout)
        self.assertIn("MASUKAN_TIDAK_VALID", result.stdout)
        self.assertNotIn("KONDISI_NORMAL", result.stdout)


    def test_decimal_reserve_within_range_uses_policy_thresholds(self):
        result = self.run_engine("20.5\nya\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AIR-03: PENGHEMATAN", result.stdout)
        self.assertIn("HEMAT_AIR", result.stdout)
        self.assertIn("Terapkan penghematan", result.stdout)

    def test_fifty_percent_boundary_and_just_above(self):
        cases = (
            ("50\nya\n", "AIR-03: PENGHEMATAN", "HEMAT_AIR"),
            ("50.1\nya\n", "AIR-04: KONDISI_NORMAL", "KONDISI_NORMAL"),
        )
        for user_input, rule, decision in cases:
            with self.subTest(user_input=user_input):
                result = self.run_engine(user_input)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(rule, result.stdout)
                self.assertIn(decision, result.stdout)

    def test_non_finite_decimal_is_rejected_before_policy_decision(self):
        for value in ("NaN", "inf", "-Infinity"):
            with self.subTest(value=value):
                result = self.run_engine(f"{value}\nya\n")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Input tidak valid:", result.stdout)
                self.assertIn("Masukkan cadangan sebagai angka yang valid", result.stdout)
                self.assertNotIn("AIR-01:", result.stdout)
                self.assertNotIn("AIR-03:", result.stdout)
                self.assertNotIn("AIR-04:", result.stdout)

    def test_invalid_basic_needs_answer_uses_invalid_input_rule(self):
        result = self.run_engine("15\nmungkin\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AIR-00: INPUT_KEBUTUHAN_TIDAK_VALID", result.stdout)
        self.assertIn("MASUKAN_TIDAK_VALID", result.stdout)
        self.assertIn("jawab kebutuhan dasar dengan ya atau tidak", result.stdout)
        self.assertIn("Konfirmasi apakah kebutuhan dasar", result.stdout)
        self.assertNotIn("KONDISI_NORMAL", result.stdout)

    def test_malformed_decimal_is_caught_without_a_policy_decision(self):
        result = self.run_engine("bukan-angka\nya\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Input tidak valid:", result.stdout)
        self.assertIn("Masukkan cadangan sebagai angka yang valid", result.stdout)
        self.assertNotIn("AIR-01:", result.stdout)
        self.assertNotIn("AIR-04:", result.stdout)

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


    def test_unknown_rule_id_never_defaults_to_normal_decision(self):
        source = EXAMPLE.read_text(encoding="utf-8")
        function_definitions = source.split("\ncoba\n", 1)[0]
        probe = function_definitions + """
hedeh keputusan_dari_aturan("UNKNOWN")
hedeh alasan_dari_aturan("UNKNOWN")
hedeh tindakan_dari_aturan("UNKNOWN")
selesai jancuk
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            program = Path(temp_dir) / "unknown_rule_probe.cuk"
            program.write_text(probe, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), str(program)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ATURAN_TIDAK_DIKENAL", result.stdout)
        self.assertIn("ID aturan tidak dikenal", result.stdout)
        self.assertIn("periksa ID aturan sebelum tindakan", result.stdout)
        self.assertNotIn("KONDISI_NORMAL", result.stdout)


if __name__ == "__main__":
    unittest.main()
