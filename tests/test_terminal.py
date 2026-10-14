"""Tes integrasi terminal Pusingcuk untuk alur yang paling umum."""
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERMINAL = ROOT / "terminal.py"


class TerminalTests(unittest.TestCase):
    def run_terminal(self, typed_text):
        return subprocess.run(
            [sys.executable, str(TERMINAL)],
            input=typed_text,
            text=True,
            capture_output=True,
            cwd=ROOT,
            timeout=5,
            check=False,
        )

    def test_contoh_command_executes_and_prints_seven(self):
        result = self.run_terminal(":contoh\n:keluar\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Pusingcuk Terminal 0.5-dev", result.stdout)
        self.assertRegex(result.stdout, r"7\npusingcuk>")
        self.assertIn("Sampai jumpa!", result.stdout)

    def test_custom_program_runs_and_prints_result(self):
        source = (
            "jancuk\n"
            "lah angka = 3 + 4\n"
            "hedeh angka\n"
            "selesai jancuk\n"
            ":keluar\n"
        )
        result = self.run_terminal(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"7\npusingcuk>")

    def test_variables_persist_between_submissions(self):
        source = (
            "jancuk\nlah saldo = 100\nhedeh saldo\nselesai jancuk\n"
            "jancuk\nsaldo = saldo + 50\nhedeh saldo\nselesai jancuk\n:keluar\n"
        )
        result = self.run_terminal(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("100\n", result.stdout)
        self.assertIn("150\n", result.stdout)

    def test_functions_persist_between_submissions(self):
        source = (
            "jancuk\nfungsi gandakan(n)\n    balek n * 2\nselesai fungsi\nselesai jancuk\n"
            "jancuk\nhedeh gandakan(21)\nselesai jancuk\n:keluar\n"
        )
        result = self.run_terminal(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"42\npusingcuk>")

    def test_tanya_reads_terminal_input(self):
        source = (
            "jancuk\n"
            'tanya nama = "Nama kamu? "\n'
            'hedeh "Halo, " + nama\n'
            "selesai jancuk\n"
            "Budi\n"
            ":keluar\n"
        )
        result = self.run_terminal(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Nama kamu?", result.stdout)
        self.assertIn("Halo, Budi", result.stdout)


if __name__ == "__main__":
    unittest.main()
