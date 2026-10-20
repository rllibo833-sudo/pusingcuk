"""Conformance checks for portable JSON, HTML escaping, and CSV row built-ins."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from compiler.ir import from_source
from compiler.js_backend import generate
from library.stdlib import call_builtin

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
SOURCE = (ROOT / "tests" / "conformance" / "formats_json_html_csv.cuk").read_text(encoding="utf-8")


class FormatBuiltinTests(unittest.TestCase):
    def test_reference_json_html_and_csv_contract(self):
        value = {"nama": "Budi", "aktif": True}
        self.assertEqual(call_builtin("json_teks", value), '{"nama":"Budi","aktif":true}')
        self.assertEqual(call_builtin("json_baca", '{"nama":"Budi","aktif":true}'), value)
        self.assertEqual(call_builtin("html_aman", "<b>&\"'"), "&lt;b&gt;&amp;&quot;&#x27;")
        self.assertEqual(call_builtin("csv_baris", ["Budi", "kopi, susu", 'dia bilang "hai"']),
                         'Budi,"kopi, susu","dia bilang ""hai"""')

    def test_json_rejects_unsafe_values_and_bad_input(self):
        for value in ({"angka": 9007199254740992}, {"angka": float("inf")}, {1: "bukan kunci teks"}):
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                call_builtin("json_teks", value)
        with self.assertRaises(ValueError):
            call_builtin("json_baca", '{"broken":')


    def test_json_rejects_invalid_values_and_serializes_nested_values(self):
        nested = {"items": [1, {"ok": True}], "empty": None}
        encoded = call_builtin("json_teks", nested)
        self.assertEqual(encoded, '{"items":[1,{"ok":true}],"empty":null}')
        self.assertEqual(call_builtin("json_teks", {"integer_float": 1.0, "negative_zero": -0.0}), '{"integer_float":1,"negative_zero":0}')
        self.assertEqual(call_builtin("csv_baris", [1.0, 0.5]), "1,0.5")
        self.assertEqual(call_builtin("html_aman", 1.0), "1")
        self.assertEqual(call_builtin("json_baca", encoded), nested)
        for invalid in ("not json", '{"x":}', '{"x":1,}', "01", "NaN", "Infinity"):
            with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                call_builtin("json_baca", invalid)
        with self.assertRaises(ValueError):
            call_builtin("json_baca", "9007199254740992")
        with self.assertRaises(ValueError):
            call_builtin("json_teks", {"nested": [9007199254740992]})

    def test_csv_quotes_newline_and_carriage_return(self):
        self.assertEqual(call_builtin("csv_baris", ["line\nbreak", "carriage\rreturn"]),
                         '"line\nbreak","carriage\rreturn"')

    @unittest.skipUnless(NODE, "Node.js tidak tersedia")
    def test_javascript_backend_matches_format_fixture(self):
        generated = generate(from_source(SOURCE, "formats_json_html_csv.cuk"))
        with tempfile.TemporaryDirectory(prefix="pusingcuk-formats-") as temp:
            path = Path(temp) / "formats.js"
            path.write_text(generated, encoding="utf-8")
            result = subprocess.run([NODE, str(path)], text=True, capture_output=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '{"nama":"Budi","aktif":true}\nBudi\nSiti\nokelah\n&lt;b&gt;&amp;&quot;&#x27;\nBudi,"kopi, susu","dia bilang ""hai"""\n')


if __name__ == "__main__":
    unittest.main()
