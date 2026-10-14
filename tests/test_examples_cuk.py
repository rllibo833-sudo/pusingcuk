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
        self.assertIn("OUTPUT_MENUNGGU_TINJAUAN", output)
        self.assertIn(
            "Gunakan konteks terverifikasi saja. Konteks: Kontrak runtime lokal. Pertanyaan: Apa batas tool?",
            output,
        )

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
