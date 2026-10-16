"""Regression tests for launching the interactive REPL from the default CLI."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReplEntryPointTests(unittest.TestCase):
    def test_no_arguments_starts_repl(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "pusingcuk_new.py")],
            input=":keluar\n",
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Pusingcuk Terminal 0.6-dev", result.stdout)
        self.assertIn("Sampai jumpa!", result.stdout)

    def test_check_without_file_still_errors(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "pusingcuk_new.py"), "--check"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("membutuhkan berkas sumber", result.stderr)


if __name__ == "__main__":
    unittest.main()
