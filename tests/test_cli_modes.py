"""Regression tests for beginner-friendly CLI modes and the canonical .cuk suffix."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"


class CLIModeTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CLI), *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )

    def test_cuk_file_executes(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "program.cuk"
            source.write_text(
                'jancuk\nhedeh "Halo dari .cuk"\nselesai jancuk\n',
                encoding="utf-8",
            )
            result = self.run_cli(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Halo dari .cuk\n")
        self.assertEqual(result.stderr, "")

    def test_check_mode_parses_without_executing_program(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.cuk"
            source.write_text(
                'jancuk\ntanya nama = "Masukkan nama: "\n'
                'hedeh nama\nselesai jancuk\n',
                encoding="utf-8",
            )
            result = self.run_cli("--check", source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: sintaks valid", result.stdout)
        self.assertNotIn("Masukkan nama:", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_check_mode_reports_syntax_error_with_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "broken.cuk"
            source.write_text("jancuk\nhedeh )\nselesai jancuk\n", encoding="utf-8")
            result = self.run_cli("--check", source)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("Kesalahan sintaks", result.stderr)
        self.assertIn("broken.cuk", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_check_and_formatter_modes_are_mutually_exclusive(self):
        result = self.run_cli("--check", "--fmt", "halo.cuk")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not allowed with argument", result.stderr)


if __name__ == "__main__":
    unittest.main()
