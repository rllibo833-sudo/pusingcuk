"""CLI tests for beginner-facing .cuk examples."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"
EXAMPLES = ROOT / "examples"


class CukExampleCliTests(unittest.TestCase):
    def run_example(self, name, user_input):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-example-") as temporary:
            project = Path(temporary)
            script = project / name
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_bytes((EXAMPLES / name).read_bytes())
            script.chmod(0o755)
            result = subprocess.run(
                [sys.executable, str(CLI), str(script)],
                cwd=project,
                input=user_input,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            note_path = project / "keuangan_sederhana.txt"
            note = note_path.read_text(encoding="utf-8") if note_path.is_file() else None
            note_inside_project = note_path.resolve().is_relative_to(project)
            return result.stdout, note, note_inside_project

    def test_ai_engine_contract_example_runs_without_provider_or_network(self):
        output, _, _ = self.run_example("ai/engine_contract.cuk", "")
        for expected_status in (
            "OUTPUT_MENUNGGU_TINJAUAN",
            "KOMPILASI_LOLOS_RUNTIME_BELUM_DIUJI",
            "RUNTIME_TERUJI",
            "SOURCE_DITOLAK_COMPILER",
            "RUNTIME_GAGAL",
            "STATUS_KOMPILASI_TIDAK_VALID",
            "STATUS_RUNTIME_TIDAK_VALID",
        ):
            with self.subTest(expected_status=expected_status):
                self.assertIn(expected_status, output)
        self.assertIn(
            "Gunakan konteks terverifikasi saja. Konteks: Kontrak runtime lokal. Pertanyaan: Apa batas tool?",
            output,
        )

    def test_reality_engine_uses_live_input_and_explains_decision(self):
        output, _, _ = self.run_example("reality_engine.cuk", "15\nya\n")
        self.assertIn("Cadangan air saat ini (0-100%)", output)
        self.assertIn("Kebutuhan dasar masih harus dipenuhi?", output)
        self.assertIn("Cadangan air (%):", output)
        self.assertIn("15", output)
        self.assertIn("PRIORITASKAN_KEBUTUHAN_DASAR", output)
        self.assertIn("Cadangan <= 20%; kebutuhan dasar diprioritaskan.", output)
        self.assertNotIn("SIMULASI KONFLIK", output)

    def test_reality_engine_rejects_out_of_range_reserve(self):
        output, _, _ = self.run_example("reality_engine.cuk", "101\ntidak\n")
        self.assertIn("MASUKAN_TIDAK_VALID", output)
        self.assertIn("Input tidak valid: cadangan harus 0 sampai 100%.", output)

    def test_reality_engine_rejects_invalid_basic_need_answer(self):
        output, _, _ = self.run_example("reality_engine.cuk", "40\nmungkin\n")
        self.assertIn("MASUKAN_TIDAK_VALID", output)
        self.assertIn("jawab kebutuhan dasar dengan ya atau tidak", output)

    def test_reality_engine_rejects_non_numeric_reserve(self):
        output, _, _ = self.run_example("reality_engine.cuk", "abc\n")
        self.assertIn("Input tidak valid:", output)
        self.assertIn("Masukkan cadangan sebagai angka yang valid dari 0 sampai 100.", output)
        self.assertNotIn("KONDISI_NORMAL", output)
        self.assertNotIn("Cadangan air (%):", output)


    def test_reality_engine_reports_a_traceable_rule_identifier(self):
        output, _, _ = self.run_example("reality_engine.cuk", "15\nya\n")
        self.assertIn("Aturan yang cocok:", output)
        self.assertIn("AIR-01: CADANGAN_RENDAH_KEBUTUHAN_DASAR", output)

    def test_reality_engine_rule_ids_match_all_policy_outcomes(self):
        cases = (
            ("20\nya\n", "AIR-01: CADANGAN_RENDAH_KEBUTUHAN_DASAR", "PRIORITASKAN_KEBUTUHAN_DASAR"),
            ("20\ntidak\n", "AIR-02: CADANGAN_RENDAH_BATASI_NON_ESENSIAL", "BATASI_PENGGUNAAN_NON_ESENSIAL"),
            ("21\nya\n", "AIR-03: PENGHEMATAN", "HEMAT_AIR"),
            ("50\ntidak\n", "AIR-03: PENGHEMATAN", "HEMAT_AIR"),
            ("51\ntidak\n", "AIR-04: KONDISI_NORMAL", "KONDISI_NORMAL"),
            ("101\nya\n", "AIR-00: INPUT_CADANGAN_TIDAK_VALID", "MASUKAN_TIDAK_VALID"),
            ("40\nmungkin\n", "AIR-00: INPUT_KEBUTUHAN_TIDAK_VALID", "MASUKAN_TIDAK_VALID"),
        )
        for user_input, expected_rule, expected_decision in cases:
            with self.subTest(user_input=user_input):
                output, _, _ = self.run_example("reality_engine.cuk", user_input)
                self.assertIn(expected_rule, output)
                self.assertIn(expected_decision, output)

    def test_reality_engine_at_20_percent_prioritizes_basic_needs(self):
        output, _, _ = self.run_example("reality_engine.cuk", "20\nya\n")
        self.assertIn("PRIORITASKAN_KEBUTUHAN_DASAR", output)
        self.assertIn("Amankan air untuk minum, sanitasi, dan kebutuhan dasar", output)

    def test_reality_engine_at_20_percent_restricts_nonessential_use(self):
        output, _, _ = self.run_example("reality_engine.cuk", "20\ntidak\n")
        self.assertIn("BATASI_PENGGUNAAN_NON_ESENSIAL", output)
        self.assertIn("Batasi pemakaian non-esensial", output)

    def test_reality_engine_at_21_percent_enters_saving_mode(self):
        output, _, _ = self.run_example("reality_engine.cuk", "21\nya\n")
        self.assertIn("HEMAT_AIR", output)
        self.assertIn("Terapkan penghematan", output)

    def test_reality_engine_at_50_percent_stays_in_saving_mode(self):
        output, _, _ = self.run_example("reality_engine.cuk", "50\ntidak\n")
        self.assertIn("HEMAT_AIR", output)
        self.assertIn("Terapkan penghematan", output)

    def test_reality_engine_above_50_percent_returns_normal_guidance(self):
        output, _, _ = self.run_example("reality_engine.cuk", "51\ntidak\n")
        self.assertIn("KONDISI_NORMAL", output)
        self.assertIn("Pertahankan pemantauan berkala", output)

    def test_terminal_bot_handles_interactive_answers(self):
        output, _, _ = self.run_example("terminal_bot.cuk", "Ayu\nbaik\n")
        self.assertIn("Halo, Ayu!", output)
        self.assertIn("Senang mendengarnya", output)

    def test_halo_dunia_accepts_interactive_name(self):
        output, _, _ = self.run_example("halo_dunia.cuk", "Ayu\n")
        self.assertIn("Halo, Ayu!", output)

    def test_keuangan_example_runs_and_writes_within_project(self):
        output, note, note_inside_project = self.run_example(
            "keuangan_sederhana.cuk", "Ayu\n3000000\n1250000\nya\n"
        )
        self.assertIn("Pemasukan: 3000000", output)
        self.assertIn("Pengeluaran: 1250000", output)
        self.assertIn("Sisa: 1750000", output)
        self.assertIn("Hitung catatan ke-1", output)
        self.assertIn("Hitung catatan ke-2", output)
        self.assertIn("Status: anggaran aman", output)
        self.assertIn("Catatan tersimpan: keuangan_sederhana.txt", output)
        self.assertIsNotNone(note)
        self.assertIn("Nama: Ayu", note)
        self.assertIn("Sisa: 1750000", note)
        self.assertTrue(note_inside_project)

    def test_calculator_uses_canonical_keywords_and_adds_numbers(self):
        output, _, _ = self.run_example("kalkulator.cuk", "20\n+\n22\n")
        self.assertIn("Hasil: 42", output)

    def test_calculator_handles_division_by_zero(self):
        output, _, _ = self.run_example("kalkulator.cuk", "10\n/\n0\n")
        self.assertIn("pembagian dengan nol", output)

    def test_calculator_reports_non_numeric_input_with_next_step(self):
        output, _, _ = self.run_example("kalkulator.cuk", "dua puluh\n+\n22\n")
        self.assertIn("Input tidak valid:", output)
        self.assertIn("Masukkan bilangan yang valid", output)


if __name__ == "__main__":
    unittest.main()
