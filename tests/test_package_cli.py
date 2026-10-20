"""Package import and CLI contract tests."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackageCliTests(unittest.TestCase):
    def test_package_interpreter_import_has_no_output(self):
        result = subprocess.run(
            [sys.executable, "-c", "from pusingcuk import interpreter; assert callable(interpreter.run)"],
            cwd=ROOT, text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_module_cli_runs_existing_source_file(self):
        result = subprocess.run(
            [sys.executable, "-m", "pusingcuk.cli", "run", "examples/compat/halo.pusingcuk"],
            cwd=ROOT, text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Halo, Dunia", result.stdout)
        self.assertIn("42", result.stdout)


if __name__ == "__main__":
    unittest.main()
