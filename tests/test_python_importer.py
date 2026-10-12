"""Tests for the experimental Python-to-Pusingcuk source importer."""
import subprocess
import unittest

from compiler.import_python import ImportErrorPython, translate
from compiler.ir import from_source
from compiler.__main__ import compile_source
from compiler.js_backend import generate as generate_js
from parser import parse
from library.stdlib import BUILTINS, call_builtin


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
        self.assertIn("pcRange", generate_js(from_source(result)))

    def test_numeric_builtins_map_to_supported_stdlib(self):
        result = translate(
            "print(abs(-8))\n"
            "print(round(2.5))\n"
            "print(min(4, 9))\n"
            "print(max(4, 9))\n"
        )
        self.assertIn("hedeh mutlak((-8))", result)
        self.assertIn("hedeh bulatkan(2.5)", result)
        self.assertIn("hedeh minimum(4, 9)", result)
        self.assertIn("hedeh maksimum(4, 9)", result)
        parse(result)
        generated = generate_js(from_source(result))
        self.assertIn("pcAbs", generated)
        self.assertIn("pcRound", generated)
        self.assertIn("pcMin", generated)
        self.assertIn("pcMax", generated)

    def test_numeric_builtin_arity_is_checked(self):
        with self.assertRaises(ImportErrorPython):
            translate("print(min(1))\n")
        with self.assertRaises(ImportErrorPython):
            translate("print(round(1, 2))\n")

    def test_elif_structure(self):
        result = translate(
            "score = 8\n"
            "if score > 8:\n"
            "    print('tinggi')\n"
            "elif score == 8:\n"
            "    print('pas')\n"
            "else:\n"
            "    print('rendah')\n"
        )
        self.assertIn("kampret", result)
        parse(result)

    def test_input(self):
        result = translate("name = input('Nama? ')\nprint(name)\n")
        self.assertIn('tanya name = "Nama? "', result)
        parse(result)

    def test_math_module_maps_to_cross_target_builtins(self):
        source = (
            "import math as m\n"
            "from math import sqrt as akar_lokal, pi\n"
            "print(m.sqrt(81))\n"
            "print(akar_lokal(25))\n"
            "print(m.floor(2.9))\n"
            "print(m.ceil(2.1))\n"
            "print(m.pow(2, 3))\n"
            "print(m.sin(0))\n"
            "print(m.cos(0))\n"
            "print(m.fabs(-4))\n"
            "print(pi)\n"
        )
        translated = translate(source)
        self.assertIn("akar(", translated)
        self.assertIn("bawah(", translated)
        self.assertIn("atas(", translated)
        self.assertIn("pangkat(", translated)
        self.assertIn("sinus(", translated)
        self.assertIn("kosinus(", translated)
        parse(translated)

        generated_js = generate_js(from_source(translated))
        result = subprocess.run(
            ["node", "-e", generated_js], capture_output=True, text=True, check=True
        )
        expected = "9\n5\n2\n3\n8\n0\n1\n4\n3.141592653589793\n"
        self.assertEqual(result.stdout, expected)

        generated_html = compile_source(translated, "math_import.cuk", "html")
        self.assertIn("<script>", generated_html)
        self.assertIn("const pcSqrt", generated_html)
        self.assertIn("const pcPow", generated_html)
        script = generated_html.split("<script>\n", 1)[1].split("\n</script>", 1)[0]
        harness = (
            "global.__pc = {textContent: ''};\n"
            "global.document = {getElementById: () => global.__pc};\n"
            + script
            + "\nprocess.stdout.write(global.__pc.textContent);\n"
        )
        html_result = subprocess.run(
            ["node", "-e", harness], capture_output=True, text=True, check=True
        )
        self.assertEqual(html_result.stdout, expected)

    def test_statistics_module_maps_to_js_html_and_python(self):
        source = (
            "import statistics as stats\n"
            "from statistics import mean as average, median\n"
            "print(stats.mean([1, 2, 6]))\n"
            "print(stats.median([1, 4, 8]))\n"
            "print(median([1, 2, 3, 4]))\n"
            "print(average([2, 4]))\n"
            "print(stats.mean([9007199254740991, 9007199254740991]))\n"
        )
        translated = translate(source)
        self.assertIn("rata_rata([1, 2, 6])", translated)
        self.assertIn("median([1, 2, 3, 4])", translated)
        parse(translated)
        expected = "3\n4\n2.5\n3\n9007199254740991\n"

        generated_js = generate_js(from_source(translated))
        js_result = subprocess.run(
            ["node", "-e", generated_js], capture_output=True, text=True, check=True
        )
        self.assertEqual(js_result.stdout, expected)

        generated_html = compile_source(translated, "statistics_import.cuk", "html")
        self.assertIn("const pcMean", generated_html)
        self.assertIn("const pcMedian", generated_html)
        script = generated_html.split("<script>\n", 1)[1].split("\n</script>", 1)[0]
        harness = (
            "global.__pc = {textContent: ''};\n"
            "global.document = {getElementById: () => global.__pc};\n"
            + script
            + "\nprocess.stdout.write(global.__pc.textContent);\n"
        )
        html_result = subprocess.run(
            ["node", "-e", harness], capture_output=True, text=True, check=True
        )
        self.assertEqual(html_result.stdout, expected)

        from compiler.python_backend import generate as generate_python
        python_result = subprocess.run(
            ["python", "-c", generate_python(from_source(translated))],
            capture_output=True, text=True, check=True
        )
        self.assertEqual(python_result.stdout, expected)

    def test_statistics_runtime_rejects_invalid_samples_on_js_html_and_python(self):
        from compiler.python_backend import generate as generate_python
        cases = (
            "hedeh rata_rata([])",
            "hedeh median([1, benar])",
            'hedeh median([1, "x"])',
        )
        for statement in cases:
            source = "jancuk\n" + statement + "\nselesai jancuk"
            generated_js = generate_js(from_source(source))
            js_result = subprocess.run(
                ["node", "-e", generated_js], capture_output=True, text=True
            )
            self.assertNotEqual(js_result.returncode, 0, statement)
            self.assertEqual(js_result.stdout, "", statement)

            generated_python = generate_python(from_source(source))
            py_result = subprocess.run(
                ["python", "-c", generated_python], capture_output=True, text=True
            )
            self.assertNotEqual(py_result.returncode, 0, statement)
            self.assertEqual(py_result.stdout, "", statement)

            generated_html = compile_source(source, "invalid_statistics.cuk", "html")
            script = generated_html.split("<script>\n", 1)[1].split("\n</script>", 1)[0]
            harness = (
                "global.__pc = {textContent: ''};\n"
                "global.document = {getElementById: () => global.__pc};\n"
                + script
                + "\nprocess.stdout.write(global.__pc.textContent);\n"
            )
            html_result = subprocess.run(
                ["node", "-e", harness], capture_output=True, text=True
            )
            self.assertNotEqual(html_result.returncode, 0, statement)
            self.assertEqual(html_result.stdout, "", statement)

    def test_statistics_module_is_explicitly_allow_listed(self):
        with self.assertRaisesRegex(ImportErrorPython, "statistics.variance"):
            translate("import statistics\nprint(statistics.variance([1, 2, 3]))\n")
        with self.assertRaises(ImportErrorPython):
            translate("from statistics import *\n")
        with self.assertRaises(ImportErrorPython):
            translate("import json\n")
        with self.assertRaises(ImportErrorPython):
            translate("print(median())\n")

    def test_statistics_builtins_exist_in_standard_library_registry(self):
        self.assertIn("rata_rata", BUILTINS)
        self.assertIn("median", BUILTINS)
        self.assertEqual(call_builtin("rata_rata", [1, 2, 6]), 3)
        self.assertEqual(call_builtin("median", [1, 2, 3, 4]), 2.5)
        self.assertEqual(call_builtin("median", [1, 4, 8]), 4)
        with self.assertRaises(TypeError):
            call_builtin("rata_rata", [])
        with self.assertRaises(TypeError):
            call_builtin("median", [1, True])

    def test_math_builtins_exist_in_standard_library_registry(self):
        for name in ("akar", "bawah", "atas", "pangkat", "sinus", "kosinus"):
            self.assertIn(name, BUILTINS)
        self.assertEqual(call_builtin("akar", 81), 9)
        self.assertEqual(call_builtin("bawah", 2.9), 2)
        self.assertEqual(call_builtin("atas", 2.1), 3)
        self.assertEqual(call_builtin("pangkat", 2, 3), 8)
        self.assertEqual(call_builtin("sinus", 0), 0)
        self.assertEqual(call_builtin("kosinus", 0), 1)
        with self.assertRaises(TypeError):
            call_builtin("akar", True)

    def test_math_import_is_allow_list_only(self):
        with self.assertRaises(ImportErrorPython):
            translate("import os\n")
        with self.assertRaises(ImportErrorPython):
            translate("import math\nprint(math.log(10))\n")
        with self.assertRaises(ImportErrorPython):
            translate("from math import *\n")

    def test_rejects_chained_comparison(self):
        with self.assertRaises(ImportErrorPython):
            translate("print(1 < x < 3)\n")


if __name__ == "__main__":
    unittest.main()
