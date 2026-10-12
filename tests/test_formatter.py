"""Tests for the Pusingcuk source formatter and --fmt CLI."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.formatter import format_source


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"


class FormatterTests(unittest.TestCase):
    def test_two_space_indent_and_aligned_selesai(self):
        source = (
            "jancuk\n"
            "lah x = 1\n"
            "njir benar\n"
            "hedeh \"nested\"\n"
            "selesai njir\n"
            "selesai jancuk\n"
        )
        expected = (
            "jancuk\n"
            "  lah x = 1\n"
            "  njir benar\n"
            "    hedeh \"nested\"\n"
            "  selesai njir\n"
            "selesai jancuk\n"
        )
        self.assertEqual(format_source(source), expected)

    def test_formatter_is_idempotent(self):
        source = "jancuk\nlah x = 1\nnjir benar\n hedeh x\nselesai njir\nselesai jancuk"
        once = format_source(source)
        self.assertEqual(format_source(once), once)

    def test_cli_fmt_rewrites_file(self):
        source = "jancuk\nlah x = 1\nselesai jancuk"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.pusingcuk"
            path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "--fmt", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            formatted = path.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(formatted, "jancuk\n  lah x = 1\nselesai jancuk\n")
        self.assertIn("Format selesai", result.stdout)

    def test_nested_blocks_format_and_parse(self):
        source = (
            "jancuk\n"
            "fungsi hitung(x)\n"
            "njir x > 0\n"
            "coba\n"
            "mumet x > 1\n"
            "hedeh x\n"
            "selesai mumet\n"
            "ketangkep err\n"
            "hedeh err\n"
            "akhirnya\n"
            "hedeh \"done\"\n"
            "selesai coba\n"
            "kampret\n"
            "untuk item dalam [1, 2]\n"
            "hedeh item\n"
            "selesai untuk\n"
            "selesai njir\n"
            "balek x\n"
            "selesai fungsi\n"
            "selesai jancuk\n"
        )
        formatted = format_source(source)
        from parser import parse
        parse(formatted)
        self.assertIn("        mumet x > 1\n", formatted)
        self.assertIn("          hedeh x\n", formatted)
        self.assertIn("      ketangkep err\n", formatted)
        self.assertIn("    kampret\n", formatted)
        self.assertIn("      untuk item dalam [1, 2]\n", formatted)

    def test_invalid_syntax_is_rejected_without_modifying_source(self):
        from parser import ParserError
        from tools.formatter import format_file
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.pusingcuk"
            original = "jancuk\nlah x =\nselesai jancuk\n"
            path.write_text(original, encoding="utf-8")
            with self.assertRaises(ParserError):
                format_file(path)
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertFalse(path.with_suffix(".pusingcuk.bak").exists())

    def test_formatter_creates_exact_backup(self):
        from tools.formatter import format_file
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.pusingcuk"
            original = "jancuk\nlah x = 1\nselesai jancuk"
            path.write_text(original, encoding="utf-8")
            format_file(path)
            self.assertEqual(
                path.with_suffix(".pusingcuk.bak").read_text(encoding="utf-8"),
                original,
            )
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "jancuk\n  lah x = 1\nselesai jancuk\n",
            )

    def test_cli_fmt_rejects_non_pusingcuk_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text("hello", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "--fmt", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn(".pusingcuk", result.stderr)


if __name__ == "__main__":
    unittest.main()
