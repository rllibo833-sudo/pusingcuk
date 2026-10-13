"""End-to-end assertions for useful CLI parser diagnostics."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"


class CliDiagnosticTests(unittest.TestCase):
    def test_cli_reports_one_syntax_heading_with_location_and_next_step(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-parser-") as temporary:
            source = Path(temporary) / "invalid.cuk"
            source.write_text(
                "jancuk\nhedeh 1 +\nselesai jancuk\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(CLI), "--check", str(source)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr.count("Kesalahan sintaks:"), 1)
            self.assertIn(str(source), result.stderr)
            self.assertIn("Baris 2, kolom", result.stderr)
            self.assertIn("Saran:", result.stderr)
            self.assertIn("^", result.stderr)


if __name__ == "__main__":
    unittest.main()
