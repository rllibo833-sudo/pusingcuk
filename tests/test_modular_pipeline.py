"""Tes langsung untuk pipeline modular lexer -> parser -> evaluator.

Tes ini sengaja terpisah dari tests/test_interpreter.py agar CI tidak
menganggap interpreter legacy sebagai bukti pipeline modular bekerja.
"""
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from lexer import LexerError, lex
from parser import ParserError, parse
from evaluator import Evaluator, capture


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"


class ModularPipelineTests(unittest.TestCase):
    def test_lexer_recognizes_keywords_literals_and_operators(self):
        tokens = lex('lah nilai = 12 + 3.5 dan benar # komentar')
        observed = [(token.kind, token.value) for token in tokens]
        self.assertEqual(
            observed,
            [
                ("KEYWORD", "lah"),
                ("IDENT", "nilai"),
                ("OP", "="),
                ("INTEGER", 12),
                ("OP", "+"),
                ("FLOAT", 3.5),
                ("KEYWORD", "dan"),
                ("KEYWORD", "benar"),
                ("EOF", None),
            ],
        )

    def test_lexer_reports_unknown_character_with_location(self):
        with self.assertRaisesRegex(LexerError, r"Baris 1, kolom 1"):
            lex("@")

    def test_lexer_rejects_unterminated_string(self):
        with self.assertRaisesRegex(LexerError, "string belum ditutup"):
            lex('"belum selesai')

    def test_parser_requires_program_opening_and_closing(self):
        with self.assertRaises(ParserError):
            parse('hedeh "tanpa pembuka"')
        with self.assertRaises(ParserError):
            parse('jancuk\nhedeh "tanpa penutup"')

    def test_parser_produces_program_ast(self):
        tree = parse('jancuk\nlah angka = 7\nselesai jancuk')
        self.assertEqual(tree.kind, "Program")
        self.assertEqual(len(tree.body), 1)
        self.assertEqual(tree.body[0].kind, "Declare")
        self.assertEqual(tree.body[0].name, "angka")

    def test_modular_evaluator_prints_and_assigns_variables(self):
        source = """jancuk
lah angka = 4
angka = angka * 3
hedeh angka
selesai jancuk"""
        self.assertEqual(capture(source), "12\n")

    def test_modular_evaluator_supports_condition_and_loop(self):
        source = """jancuk
lah i = 1
mumet i <= 3
    njir i == 2
        hedeh "dua"
    kampret
        hedeh i
    selesai njir
    i = i + 1
selesai mumet
selesai jancuk"""
        self.assertEqual(capture(source), "1\ndua\n3\n")

    def test_modular_evaluator_supports_user_functions(self):
        source = """jancuk
fungsi tambah(a, b)
    balek a + b
selesai fungsi
hedeh tambah(2, 3)
selesai jancuk"""
        self.assertEqual(capture(source), "5\n")

    def test_modular_evaluator_supports_lists_and_length(self):
        source = """jancuk
lah angka = [10, 20, 30]
angka[1] = 25
hedeh angka[1]
hedeh panjang(angka)
selesai jancuk"""
        self.assertEqual(capture(source), "25\n3\n")

    def test_dictionary_literal_lookup_and_update(self):
        source = """jancuk
lah pengguna = {"nama": "Budi", "aktif": benar}
pengguna["nama"] = "Sari"
hedeh pengguna["nama"]
hedeh pengguna["aktif"]
hedeh panjang(pengguna)
selesai jancuk"""
        self.assertEqual(capture(source), "Sari\nokelah\n2\n")

    def test_for_loop_and_range_builtin(self):
        source = """jancuk
untuk angka dalam rentang(1, 5)
    hedeh angka
selesai untuk
selesai jancuk"""
        self.assertEqual(capture(source), "1\n2\n3\n4\n")

    def test_range_supports_step_and_negative_direction(self):
        source = """jancuk
untuk angka dalam rentang(5, 0, -2)
    hedeh angka
selesai untuk
selesai jancuk"""
        self.assertEqual(capture(source), "5\n3\n1\n")

    def test_string_index_and_length(self):
        source = """jancuk
lah kata = "pusing"
hedeh kata[1]
hedeh panjang(kata)
selesai jancuk"""
        self.assertEqual(capture(source), "u\n6\n")

    def test_dictionary_iteration_yields_keys(self):
        source = """jancuk
lah pengguna = {"nama": "Budi", "umur": 20}
untuk kunci dalam pengguna
    hedeh kunci
selesai untuk
selesai jancuk"""
        self.assertEqual(capture(source), "nama\numur\n")

    def test_empty_dictionary_and_missing_key(self):
        self.assertEqual(capture('jancuk\nlah kosong = {}\nhedeh panjang(kosong)\nselesai jancuk'), "0\n")
        source = 'jancuk\nlah pengguna = {"nama": "Budi"}\nhedeh pengguna["umur"]\nselesai jancuk'
        with self.assertRaisesRegex(RuntimeError, "kunci kamus tidak ditemukan"):
            Evaluator().run(source)

    def test_for_loop_rejects_non_iterable(self):
        source = """jancuk
untuk angka dalam 12
    hedeh angka
selesai untuk
selesai jancuk"""
        with self.assertRaisesRegex(RuntimeError, "untuk membutuhkan"):
            Evaluator().run(source)

    def test_range_rejects_zero_step(self):
        source = """jancuk
untuk angka dalam rentang(1, 4, 0)
    hedeh angka
selesai untuk
selesai jancuk"""
        with self.assertRaisesRegex(RuntimeError, "langkah rentang tidak boleh nol"):
            Evaluator().run(source)

    def test_modular_evaluator_reports_undefined_variable(self):
        source = 'jancuk\nhedeh hantu\nselesai jancuk'
        with self.assertRaisesRegex(RuntimeError, r"Baris 2: variabel 'hantu' belum dibuat"):
            Evaluator().run(source)

    def test_modular_evaluator_reports_division_by_zero(self):
        source = "jancuk\nhedeh 1 / 0\nselesai jancuk"
        with self.assertRaisesRegex(RuntimeError, r"Baris 2: operasi gagal"):
            Evaluator().run(source)

    def test_cli_executes_source_file_successfully(self):
        source = 'jancuk\nhedeh "Pusingcuk siap"\nselesai jancuk\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contoh.pusingcuk"
            path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Pusingcuk siap\n")
        self.assertEqual(result.stderr, "")

    def test_cli_returns_nonzero_for_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "tidak-ada.pusingcuk"
            result = subprocess.run(
                [sys.executable, str(CLI), str(missing)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 3)
        self.assertIn("berkas tidak ditemukan", result.stderr)
        self.assertEqual(result.stdout, "")



    def test_builtin_function_names_cannot_be_redefined(self):
        for name in ("panjang", "rentang"):
            with self.subTest(name=name):
                source = f"jancuk\nfungsi {name}(x)\n    balek x\nselesai fungsi\nselesai jancuk"
                with self.assertRaisesRegex(RuntimeError, f"nama fungsi '{name}' sudah digunakan"):
                    Evaluator().run(source)

    def test_for_loop_can_be_nested(self):
        source = """jancuk
untuk luar dalam rentang(1, 3)
    untuk dalam_angka dalam rentang(1, 3)
        hedeh luar * 10 + dalam_angka
    selesai untuk
selesai untuk
selesai jancuk"""
        self.assertEqual(capture(source), "11\n12\n21\n22\n")

    def test_dictionary_rejects_unhashable_key(self):
        source = "jancuk\nlah data = {[1, 2]: \"nilai\"}\nselesai jancuk"
        with self.assertRaisesRegex(RuntimeError, "kunci kamus harus dapat digunakan"):
            Evaluator().run(source)

    def test_range_requires_integer_arguments(self):
        source = """jancuk
untuk angka dalam rentang(1, 3.5)
    hedeh angka
selesai untuk
selesai jancuk"""
        with self.assertRaisesRegex(RuntimeError, "argumen rentang harus bilangan bulat"):
            Evaluator().run(source)



    def test_for_loop_iteration_limit(self):
        source = """jancuk
untuk angka dalam rentang(10001)
selesai untuk
selesai jancuk"""
        with self.assertRaisesRegex(RuntimeError, "batas 10000 iterasi tercapai"):
            Evaluator().run(source)

    def test_lexer_canonicalizes_genz_aliases(self):
        tokens = lex("inthiseco jir adooh gitu janggal")
        self.assertEqual(
            [(token.kind, token.value) for token in tokens],
            [
                ("KEYWORD", "jancuk"),
                ("KEYWORD", "hedeh"),
                ("KEYWORD", "kampret"),
                ("KEYWORD", "selesai"),
                ("KEYWORD", "bukan"),
                ("EOF", None),
            ],
        )

    def test_genz_aliases_work_in_the_modular_interpreter(self):
        source = """inthiseco
jir "Pusingcuk native"
jir janggal benar
njir benar
    jir "cabang utama"
adooh
    jir "salah"
gitu njir
njir salah
    jir "salah"
adooh
    jir "adooh aktif"
gitu njir
gitu inthiseco"""
        self.assertEqual(
            capture(source),
            "Pusingcuk native\ntidak\ncabang utama\nadooh aktif\n",
        )


    def test_namespaced_standard_library_uses_shared_builtin_contract(self):
        source = """jancuk
hedeh matematika.akar(81)
hedeh koleksi.jumlah([1, 2, 3, 4])
hedeh konversi.teks(42)
hedeh json.teks({"nama": "cuk"})
hedeh web.aman_html("<b>")
hedeh tabel.baris_csv(["a,b", "cuk"])
selesai jancuk"""
        self.assertEqual(
            capture(source),
            '9\\n10\\n42\\n{"nama":"cuk"}\\n&lt;b&gt;\\n"a,b",cuk\\n'
        )

    def test_namespaced_standard_library_reports_unknown_member(self):
        source = """jancuk
hedeh matematika.tidak_ada(1)
selesai jancuk"""
        with self.assertRaisesRegex(RuntimeError, "library 'matematika' tidak menyediakan 'tidak_ada'"):
            capture(source)


if __name__ == "__main__":
    unittest.main()
