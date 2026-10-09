import unittest
from contextlib import redirect_stdout
from io import StringIO

import interpreter


class PusingcukTests(unittest.TestCase):
    def run_code(self, source):
        output = StringIO()
        with redirect_stdout(output):
            interpreter.run(source)
        return output.getvalue()


    def test_list_read(self):
        code = """jancuk
lah buah = ["apel", "jeruk"]
hedeh buah[0]
hedeh buah[1]
selesai jancuk"""
        self.assertEqual(self.run_code(code), "apel\njeruk\n")
    def test_list_assignment(self):
        code = """jancuk
lah buah = ["apel", "jeruk"]
buah[1] = "durian"
hedeh buah[0]
hedeh buah[1]
selesai jancuk"""
        self.assertEqual(self.run_code(code), "apel\ndurian\n")
    def test_list_index_out_of_range(self):
        code = """jancuk
lah angka = [10]
hedeh angka[1]
selesai jancuk"""
        with self.assertRaisesRegex(SyntaxError, "indeks daftar di luar batas"):
            self.run_code(code)


    def test_list_negative_assignment_out_of_range(self):
        code = """jancuk
lah buah = ["apel"]
buah[-1] = "jeruk"
selesai jancuk"""
        with self.assertRaisesRegex(SyntaxError, "indeks daftar di luar batas"):
            self.run_code(code)

    def test_panjang_list(self):
        code = """jancuk
lah buah = ["apel", "jeruk", "durian"]
hedeh panjang(buah)
hedeh panjang([])
selesai jancuk"""
        self.assertEqual(self.run_code(code), "3\n0\n")
    def test_print(self):
        code = '''jancuk
hedeh "Halo"
selesai jancuk'''
        self.assertEqual(self.run_code(code), "Halo\n")

    def test_variable(self):
        code = '''jancuk
lah angka = 10
hedeh angka
selesai jancuk'''
        self.assertEqual(self.run_code(code), "10\n")

    def test_if_else(self):
        code = '''jancuk
lah umur = 20
njir umur >= 18
hedeh "Dewasa"
kampret
hedeh "Anak-anak"
selesai njir
selesai jancuk'''
        self.assertEqual(self.run_code(code), "Dewasa\n")

    def test_loop_and_assignment(self):
        code = '''jancuk
lah i = 1
mumet i <= 3
hedeh i
i = i + 1
selesai mumet
selesai jancuk'''
        self.assertEqual(self.run_code(code), "1\n2\n3\n")

    def test_unknown_variable(self):
        code = '''jancuk
hedeh hantu
selesai jancuk'''
        with self.assertRaisesRegex(
            SyntaxError, "belum ada"
        ):
            self.run_code(code)


    def test_if_without_closing(self):
        code = """jancuk
njir benar
hedeh "Halo"
selesai jancuk"""
        with self.assertRaises(SyntaxError):
            self.run_code(code)

    def test_else_without_if(self):
        code = """jancuk
kampret
hedeh "Halo"
selesai jancuk"""
        with self.assertRaises(SyntaxError):
            self.run_code(code)

    def test_loop_without_closing(self):
        code = """jancuk
mumet benar
hedeh "Halo"
selesai jancuk"""
        with self.assertRaises(SyntaxError):
            self.run_code(code)

    def test_wrong_block_closer(self):
        code = """jancuk
njir benar
hedeh "Halo"
selesai mumet
selesai jancuk"""
        with self.assertRaises(SyntaxError):
            self.run_code(code)

    def test_nested_if_inside_loop(self):
        code = """jancuk
lah i = 1
mumet i <= 2
njir i == 1
hedeh "satu"
kampret
hedeh "dua"
selesai njir
i = i + 1
selesai mumet
selesai jancuk"""
        self.assertEqual(self.run_code(code), "satu\ndua\n")


    def test_loop_iteration_limit(self):
        code = """jancuk
mumet benar
selesai mumet
selesai jancuk"""
        with self.assertRaises(SyntaxError) as context:
            self.run_code(code)
        self.assertIn("batas 10000 iterasi tercapai", str(context.exception))


    def test_nested_loop_total_execution_limit(self):
        code = """jancuk
lah i = 0
lah j = 0
mumet i < 400
    j = 0
    mumet j < 400
        j = j + 1
    selesai mumet
    i = i + 1
selesai mumet
selesai jancuk"""
        with self.assertRaisesRegex(
            SyntaxError, "batas total 100000 langkah tercapai"
        ):
            self.run_code(code)


    def test_unterminated_string_is_reported_as_syntax_error(self):
        code = 'jancuk\nhedeh "abc\nselesai jancuk'
        with self.assertRaisesRegex(
            SyntaxError, "ekspresi tidak valid: token tidak lengkap"
        ):
            self.run_code(code)


    def test_expression_length_limit(self):
        code = "jancuk\nhedeh \"" + "a" * 10001 + "\"\nselesai jancuk"
        with self.assertRaisesRegex(SyntaxError, "ekspresi terlalu panjang"):
            self.run_code(code)


    def test_deep_expression_is_rejected_safely(self):
        code = "jancuk\nhedeh " + "not " * 1500 + "benar\nselesai jancuk"
        with self.assertRaisesRegex(SyntaxError, "ekspresi terlalu dalam"):
            self.run_code(code)


if __name__ == "__main__":
    unittest.main()
