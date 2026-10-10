import unittest
from unittest.mock import patch
from evaluator import capture, run


def program(body):
    return "jancuk\n" + body + "\nselesai jancuk\n"


class EvaluatorTests(unittest.TestCase):
    def test_variables_and_math(self):
        self.assertEqual(capture(program(
            "lah x = 2 + 3 * 4\nhedeh x"
        )), "14\n")

    def test_list_index(self):
        self.assertEqual(capture(program(
            "lah a = [10, 20]\na[0] = 99\nhedeh a[0]\nhedeh panjang(a)"
        )), "99\n2\n")

    def test_if_and_while(self):
        self.assertEqual(capture(program(
            "lah x = 3\nmumet x > 0\nx = x - 1\nselesai mumet\n"
            "njir x == 0\nhedeh benar\nkampret\nhedeh salah\nselesai njir"
        )), "okelah\n")

    def test_function(self):
        self.assertEqual(capture(program(
            "fungsi tambah(a, b)\nbalek a + b\nselesai fungsi\n"
            "hedeh tambah(4, 5)"
        )), "9\n")

    def test_function_can_be_called_before_definition(self):
        self.assertEqual(capture(program(
            "hedeh tambah(4, 5)\n"
            "fungsi tambah(a, b)\nbalek a + b\nselesai fungsi"
        )), "9\n")

    def test_undefined_variable(self):
        with self.assertRaisesRegex(RuntimeError, "belum dibuat"):
            run(program("hedeh hilang"))

    def test_out_of_bounds(self):
        with self.assertRaisesRegex(RuntimeError, "di luar batas"):
            run(program("lah a = [1]\nhedeh a[2]"))

    def test_nested_list_assignment(self):
        self.assertEqual(capture(program(
            "lah a = [[1, 2], [3, 4]]\na[1][0] = 77\nhedeh a[1][0]"
        )), "77\n")

    def test_loop_iteration_limit(self):
        with self.assertRaisesRegex(RuntimeError, "10000 iterasi"):
            run(program(
                "lah x = 1\nmumet benar\nx = x + 1\nselesai mumet"
            ))

    def test_recursion_limit(self):
        with self.assertRaisesRegex(RuntimeError, "kedalaman"):
            run(program(
                "fungsi ulang(n)\nbalek ulang(n + 1)\nselesai fungsi\n"
                "hedeh ulang(0)"
            ))


    def test_boolean_and_number_dictionary_keys_are_distinct(self):
        self.assertEqual(capture(program(
            'lah data = {1: "angka", benar: "boolean"}\n'
            'hedeh data[1]\nhedeh data[benar]\n'
            'data[1] = "angka baru"\ndata[benar] = "boolean baru"\n'
            'hedeh panjang(data)\nhedeh benar == 1'
        )), "angka\nboolean\n2\ntidak\n")

    def test_boolean_output_format(self):
        self.assertEqual(capture(program(
            "hedeh benar\nhedeh salah"
        )), "okelah\ntidak\n")

    def test_tanya_input(self):
        source = program('tanya nama = "Nama? "\nhedeh "Halo, " + nama')
        with patch("builtins.input", return_value="Budi"):
            self.assertEqual(capture(source), "Halo, Budi\n")


if __name__ == "__main__":
    unittest.main()
