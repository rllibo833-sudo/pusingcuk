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


if __name__ == "__main__":
    unittest.main()
