import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from compiler.ir import from_source
from compiler.js_backend import JSBackendError, generate


NODE = shutil.which("node")


@unittest.skipUnless(NODE, "Node.js tidak tersedia")
class JavaScriptBackendTests(unittest.TestCase):
    def run_source(self, source, input_text=""):
        generated = generate(from_source(source, "fixture.pusingcuk"))
        with tempfile.TemporaryDirectory(prefix="pusingcuk-js-") as temp:
            path = Path(temp) / "program.js"
            path.write_text(generated, encoding="utf-8")
            return subprocess.run(
                [NODE, str(path)], input=input_text, text=True, capture_output=True,
                timeout=15, check=False,
            )

    def test_compiles_and_runs_arithmetic_and_booleans(self):
        result = self.run_source(
            "jancuk\n"
            "lah angka = 6 * 7\n"
            "angka = angka + 1\n"
            "hedeh angka\n"
            "hedeh benar == 1\n"
            "selesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "43\ntidak\n")

    def test_short_circuit_and_floor_division_match_language(self):
        result = self.run_source(
            "jancuk\n"
            "hedeh -7 // 3\n"
            "hedeh -7 % 3\n"
            "hedeh salah dan (1 // 0 == 0)\n"
            "hedeh benar atau (1 // 0 == 0)\n"
            "selesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "-3\n2\ntidak\nokelah\n")

    def test_functions_conditionals_and_loops(self):
        result = self.run_source(
            "jancuk\n"
            "fungsi tambah(a, b)\n"
            "    balek a + b\n"
            "selesai fungsi\n"
            "lah i = 1\n"
            "lah total = 0\n"
            "mumet i <= 5\n"
            "    total = total + i\n"
            "    i = i + 1\n"
            "selesai mumet\n"
            "njir total == 15\n"
            "    hedeh tambah(total, 27)\n"
            "kampret\n"
            "    hedeh 0\n"
            "selesai njir\n"
            "selesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "42\n")

    def test_lists_dictionaries_and_iteration(self):
        result = self.run_source(
            "jancuk\n"
            "lah data = [10, 20, 30]\n"
            "data[1] = 7\n"
            "hedeh data[1]\n"
            "lah kamus = {\"nama\": \"Budi\", \"umur\": 20}\n"
            "hedeh kamus[\"nama\"]\n"
            "untuk angka dalam rentang(1, 4)\n"
            "    hedeh angka\n"
            "selesai untuk\n"
            "selesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "7\nBudi\n1\n2\n3\n")

    def test_multiplication_matches_reference_for_string_and_list_repetition(self):
        result = self.run_source(
            'jancuk\nhedeh "cuk" * 3\nhedeh 3 * "x"\n'
            'hedeh [1, 2] * 2\nhedeh 2 * [7]\nselesai jancuk'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "cukcukcuk\nxxx\n[1, 2, 1, 2]\n[7, 7]\n")

        invalid = self.run_source('jancuk\nhedeh "cuk" * 1.5\nselesai jancuk')
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("operator *", invalid.stderr)

    def test_subtraction_and_division_reject_javascript_type_coercion(self):
        for expression in ('"5" - 2', '"6" / 2', 'benar * 3'):
            with self.subTest(expression=expression):
                result = self.run_source(f"jancuk\nhedeh {expression}\nselesai jancuk")
                self.assertNotEqual(result.returncode, 0)

    def test_modulo_unary_minus_and_comparisons_reject_javascript_coercion(self):
        valid = self.run_source(
            'jancuk\nhedeh -7 % 3\nhedeh "apel" < "jeruk"\nhedeh 2 <= 3\nselesai jancuk'
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(valid.stdout, "2\nokelah\nokelah\n")

        for expression in ('"7" % 2', 'benar % 2', '-benar', '"7" < 8', 'benar >= 0'):
            with self.subTest(expression=expression):
                result = self.run_source(f"jancuk\nhedeh {expression}\nselesai jancuk")
                self.assertNotEqual(result.returncode, 0, expression)

    def test_unicode_string_index_and_length_use_code_points(self):
        result = self.run_source(
            'jancuk\nlah teks = "A🌾Z"\nhedeh teks[1]\nhedeh panjang(teks)\nselesai jancuk'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "🌾\n3\n")

    def test_dictionary_equality_matches_language_value_semantics(self):
        result = self.run_source(
            "jancuk\n"
            'lah pertama = {"nama": "Budi", "umur": 20}\n'
            'lah kedua = {"umur": 20, "nama": "Budi"}\n'
            'lah ketiga = {"nama": "Budi", "umur": 21}\n'
            "hedeh pertama == kedua\n"
            "hedeh pertama == ketiga\n"
            "selesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "okelah\ntidak\n")


    def test_accounting_example_runs_on_standalone_javascript(self):
        # Compile the real .cuk example to JS, then execute it without Python at runtime.
        root = Path(__file__).resolve().parents[1]
        source = (root / "examples" / "accounting" / "rekap_keuangan.cuk").read_text(encoding="utf-8")
        result = self.run_source(
            source,
            input_text="1250000\n300000\n4450000\n1500000\n2000000\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "Pendapatan (Rp): Total beban (Rp): Total aset (Rp): Total liabilitas (Rp): "
            "Ekuitas sebelum laba periode (Rp): === Ringkasan Akuntansi (Rp) ===\n"
            "Pendapatan: 1250000\nBeban: 300000\nLaba/(rugi): 950000\n"
            "Ekuitas akhir: 2950000\nSelisih posisi keuangan: 0\n"
            "Persamaan posisi keuangan seimbang.\n",
        )

    def test_javascript_conversion_builtins_enforce_shared_safe_integer_rules(self):
        result = self.run_source(
            "jancuk\n"
            "hedeh teks(benar)\n"
            "hedeh teks(salah)\n"
            "hedeh bilangan(42.9)\n"
            'hedeh bilangan("-42")\n'
            "selesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "okelah\ntidak\n42\n-42\n")

        invalid = self.run_source(
            'jancuk\nhedeh bilangan("9007199254740992")\nselesai jancuk'
        )
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("rentang aman lintas target", invalid.stderr)

    def test_accounting_source_exports_callable_javascript_module(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "examples" / "accounting" / "aturan_ringkasan.cuk").read_text(encoding="utf-8")
        generated = generate(from_source(source, "aturan_ringkasan.cuk"), as_module=True)
        with tempfile.TemporaryDirectory(prefix="pusingcuk-rules-") as temp:
            path = Path(temp) / "rules.cjs"
            path.write_text(generated, encoding="utf-8")
            result = subprocess.run(
                [NODE, "-e", "const r=require(process.argv[1]); process.stdout.write(JSON.stringify(r.hitung_ringkasan(1250000,300000,4450000,1500000,2000000)))", str(path)],
                input="", text=True, capture_output=True, timeout=15, check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "[950000,2950000,0]")

    def test_rejects_integer_outside_javascript_safe_range(self):
        with self.assertRaisesRegex(JSBackendError, "rentang aman JavaScript"):
            generate(from_source("jancuk\nhedeh 9007199254740992\nselesai jancuk"))

    def test_rejects_unknown_function_during_compilation(self):
        with self.assertRaisesRegex(JSBackendError, "tidak dikenal"):
            generate(from_source("jancuk\nhedeh fungsi_ajaib(1)\nselesai jancuk"))

    def test_input_compiles_and_runs_on_node(self):
        result = self.run_source(
            'jancuk\ntanya nama = "Nama? "\nhedeh nama\nselesai jancuk',
            input_text="Budi\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Nama? Budi\n")


    def test_try_catches_runtime_error_and_runs_finally_without_leaking_handler_name(self):
        result = self.run_source(
            "jancuk\n"
            "lah pesan = \"luar\"\n"
            "coba\n"
            "    hedeh 1 // 0\n"
            "ketangkep pesan\n"
            "    hedeh pesan\n"
            "akhirnya\n"
            "    hedeh \"akhir\"\n"
            "selesai coba\n"
            "hedeh pesan\n"
            "selesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "pembagian dengan nol\nakhir\nluar\n")

    def test_try_finally_runs_when_error_is_not_caught(self):
        result = self.run_source(
            "jancuk\ncoba\n    hedeh 1 // 0\nakhirnya\n"
            "    hedeh \"akhir\"\nselesai coba\nselesai jancuk"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "akhir\n")
        self.assertIn("pembagian dengan nol", result.stderr)

if __name__ == "__main__":
    unittest.main()
