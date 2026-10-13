"""Contract tests for .cuk and backward-compatible .pusingcuk module imports."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.__main__ import compile_source
from library.module_system import expand_file


class ModuleExtensionTests(unittest.TestCase):
    def write_program(self, path, body):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("jancuk\n" + body + "\nselesai jancuk\n", encoding="utf-8")
        return path

    def test_compiler_expands_and_runs_cuk_entry_and_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_program(
                root / "lib" / "angka.cuk",
                "ekspor fungsi tambah\n"
                "fungsi tambah(a, b)\n"
                "    balek a + b\n"
                "selesai fungsi",
            )
            entry = self.write_program(
                root / "main.cuk",
                'pakai "lib/angka.cuk" sebagai hitung\n'
                "hedeh hitung.tambah(20, 22)",
            )
            expanded = expand_file(entry)
            self.assertNotIn("pakai ", expanded)
            generated = compile_source(expanded, entry.name, "python")
            output = root / "main.py"
            output.write_text(generated, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(output)],
                text=True,
                capture_output=True,
                timeout=5,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "42\n")
        self.assertEqual(result.stderr, "")

    def test_compiler_keeps_legacy_pusingcuk_extension(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_program(
                root / "lib" / "angka.pusingcuk",
                "ekspor fungsi jawab\n"
                "fungsi jawab()\n"
                "    balek 42\n"
                "selesai fungsi",
            )
            entry = self.write_program(
                root / "main.pusingcuk",
                'pakai "lib/angka.pusingcuk" sebagai angka\n'
                "hedeh angka.jawab()",
            )
            expanded = expand_file(entry)
        self.assertNotIn("pakai ", expanded)
        self.assertIn("_pcmod_", expanded)


if __name__ == "__main__":
    unittest.main()
