import io
import unittest

from compiler.bytecode import BytecodeError, compile_source, validate_bytecode
from compiler.vm import VirtualMachine, VMError


class PortableVMTests(unittest.TestCase):
    def run_source(self, source, input_text=""):
        program = compile_source(source, "fixture.pusingcuk")
        output = io.StringIO()
        machine = VirtualMachine(program, input_stream=io.StringIO(input_text), output_stream=output)
        machine.run()
        return output.getvalue()

    def test_arithmetic_and_boolean_type_identity(self):
        self.assertEqual(self.run_source(
            "jancuk\nlah angka = 6 * 7\nangka = angka + 1\n"
            "hedeh angka\nhedeh benar == 1\nselesai jancuk"
        ), "43\ntidak\n")

    def test_short_circuit(self):
        self.assertEqual(self.run_source(
            "jancuk\nhedeh salah dan (1 // 0 == 0)\n"
            "hedeh benar atau (1 // 0 == 0)\nselesai jancuk"
        ), "tidak\nokelah\n")

    def test_functions_conditionals_and_loops(self):
        self.assertEqual(self.run_source(
            "jancuk\nfungsi tambah(a, b)\n    balek a + b\nselesai fungsi\n"
            "lah i = 1\nlah total = 0\nmumet i <= 5\n"
            "    total = total + i\n    i = i + 1\nselesai mumet\n"
            "njir total == 15\n    hedeh tambah(total, 27)\n"
            "kampret\n    hedeh 0\nselesai njir\nselesai jancuk"
        ), "42\n")

    def test_lists_dictionary_and_iteration(self):
        self.assertEqual(self.run_source(
            'jancuk\nlah data = [10, 20, 30]\ndata[1] = 7\n'
            'hedeh data[1]\nlah d = {1: "angka", benar: "boolean"}\n'
            'hedeh d[1]\nhedeh d[benar]\n'
            'untuk n dalam rentang(1, 4)\n    hedeh n\nselesai untuk\nselesai jancuk'
        ), "7\nangka\nboolean\n1\n2\n3\n")

    def test_numeric_standard_library(self):
        self.assertEqual(self.run_source(
            "jancuk\\nhedeh mutlak(-8)\\nhedeh minimum(4, 9)\\n"
            "hedeh maksimum(4, 9)\\nhedeh bulatkan(2.5)\\n"
            "hedeh bulatkan(3.5)\\nselesai jancuk"
        ), "8\\n4\\n9\\n2\\n4\\n")

    def test_numeric_standard_library_rejects_boolean(self):
        program = compile_source("jancuk\\nhedeh mutlak(benar)\\nselesai jancuk")
        with self.assertRaisesRegex(VMError, "angka finite"):
            VirtualMachine(program, output_stream=io.StringIO()).run()

    def test_input(self):
        self.assertEqual(self.run_source(
            'jancuk\ntanya nama = "Nama? "\nhedeh nama\nselesai jancuk',
            "Budi\n",
        ), "Nama? Budi\n")

    def test_rejects_malformed_bytecode(self):
        with self.assertRaises(BytecodeError):
            validate_bytecode({"format": "bad"})

    def test_instruction_budget_stops_unbounded_loop(self):
        program = compile_source("jancuk\nmumet benar\n    hedeh 1\nselesai mumet\nselesai jancuk")
        output = io.StringIO()
        machine = VirtualMachine(program, output_stream=output, max_steps=30)
        with self.assertRaisesRegex(VMError, "batas total instruksi"):
            machine.run()


if __name__ == "__main__":
    unittest.main()
