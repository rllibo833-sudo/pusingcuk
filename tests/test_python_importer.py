"""Tests for the experimental Python-to-Pusingcuk source importer."""
import unittest

from compiler.import_python import ImportErrorPython, translate
from parser import parse


class PythonImporterTests(unittest.TestCase):
    def test_arithmetic_and_output_parse(self):
        result = translate("print(3 + 4)\n")
        self.assertIn("hedeh (3 + 4)", result)
        parse(result)

    def test_variables_and_condition(self):
        result = translate(
            "score = 7\n"
            "if score >= 5:\n"
            "    print('lulus')\n"
            "else:\n"
            "    print('ulang')\n"
        )
        self.assertIn("lah score = 7", result)
        self.assertIn("njir (score >= 5)", result)
        self.assertIn("kampret", result)
        parse(result)

    def test_variable_declared_in_both_branches(self):
        result = translate(
            "flag = True\n"
            "if flag:\n"
            "    value = 1\n"
            "else:\n"
            "    value = 2\n"
            "print(value)\n"
        )
        self.assertEqual(result.count("lah value ="), 2)
        parse(result)

    def test_for_range_and_list(self):
        result = translate("numbers = [1, 2, 3]\nfor number in range(1, 4):\n    print(number)\n")
        self.assertIn("untuk number dalam rentang(1, 4)", result)
        parse(result)

    def test_input(self):
        result = translate("name = input('Nama? ')\nprint(name)\n")
        self.assertIn('tanya name = "Nama? "', result)
        parse(result)

    def test_rejects_import_instead_of_silently_ignoring(self):
        with self.assertRaises(ImportErrorPython):
            translate("import os\n")

    def test_rejects_chained_comparison(self):
        with self.assertRaises(ImportErrorPython):
            translate("print(1 < x < 3)\n")


if __name__ == "__main__":
    unittest.main()
