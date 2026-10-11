import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.ir import from_source
from compiler.python_backend import PythonBackendError, generate


class PythonBackendTests(unittest.TestCase):
    def run_source(self, source):
        output = generate(from_source(source, "fixture.pusingcuk"))
        with tempfile.TemporaryDirectory(prefix="pusingcuk-py-") as temp:
            path = Path(temp) / "program.py"
            path.write_text(output, encoding="utf-8")
            return subprocess.run([sys.executable, str(path)], text=True,
                                  capture_output=True, timeout=5, check=False)

    def test_arithmetic_and_boolean_type_identity(self):
        result = self.run_source(
            "jancuk\nlah angka = 6 * 7\nangka = angka + 1\n"
            "hedeh angka\nhedeh benar == 1\nselesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "43\ntidak\n")

    def test_functions_and_loops(self):
        result = self.run_source(
            "jancuk\nfungsi tambah(a, b)\n    balek a + b\nselesai fungsi\n"
            "lah i = 1\nlah total = 0\nmumet i <= 5\n"
            "    total = total + i\n    i = i + 1\nselesai mumet\n"
            "hedeh tambah(total, 27)\nselesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "42\n")

    def test_lists_and_index_assignment(self):
        result = self.run_source(
            "jancuk\nlah data = [10, 20, 30]\ndata[1] = 7\n"
            "hedeh data[1]\nhedeh panjang(data)\nselesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "7\n3\n")

    def test_dictionary_boolean_and_number_keys_stay_distinct(self):
        result = self.run_source(
            'jancuk\nlah d = {1: "angka", benar: "boolean"}\n'
            'hedeh d[1]\nhedeh d[benar]\nselesai jancuk'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "angka\nboolean\n")

    def test_input_is_supported(self):
        output = generate(from_source('jancuk\ntanya nama = "Nama? "\nhedeh nama\nselesai jancuk'))
        with tempfile.TemporaryDirectory(prefix="pusingcuk-py-") as temp:
            path = Path(temp) / "program.py"
            path.write_text(output, encoding="utf-8")
            result = subprocess.run([sys.executable, str(path)], input="Budi\n",
                                    text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Nama? Budi\n")

    def test_unknown_function_is_compile_error(self):
        with self.assertRaisesRegex(PythonBackendError, "tidak dikenal"):
            generate(from_source("jancuk\nhedeh ajaib(1)\nselesai jancuk"))


if __name__ == "__main__":
    unittest.main()
