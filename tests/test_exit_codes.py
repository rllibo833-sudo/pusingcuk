"""CLI exit-code contract for the modular Pusingcuk interpreter."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"


class ExitCodeTests(unittest.TestCase):
    def run_cli(self, path):
        return subprocess.run(
            [sys.executable, str(CLI), str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_missing_file_returns_3(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.pusingcuk"
            result = self.run_cli(missing)
        self.assertEqual(result.returncode, 3)
        self.assertIn("berkas tidak ditemukan", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_syntax_error_returns_2(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "syntax.pusingcuk"
            source.write_text('jancuk\nhedeh )\nselesai jancuk\n', encoding="utf-8")
            result = self.run_cli(source)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Kesalahan sintaks", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_runtime_error_returns_1(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "runtime.pusingcuk"
            source.write_text('jancuk\nhedeh nama_belum_ada\nselesai jancuk\n', encoding="utf-8")
            result = self.run_cli(source)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Kesalahan runtime", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_success_returns_0(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "success.pusingcuk"
            source.write_text('jancuk\nhedeh "berhasil"\nselesai jancuk\n', encoding="utf-8")
            result = self.run_cli(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "berhasil\n")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
