import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.c_backend import CBackendError, generate
from compiler.ir import from_source


ROOT = Path(__file__).resolve().parents[1]
COMPILER = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")


@unittest.skipUnless(COMPILER, "C11 compiler tidak tersedia")
class CBackendTests(unittest.TestCase):
    def compile_and_run(self, source):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-c-backend-") as temp:
            root = Path(temp)
            generated = root / "program.c"
            executable = root / "program"
            generated.write_text(generate(from_source(source, "fixture.pusingcuk")), encoding="utf-8")
            built = subprocess.run(
                [COMPILER, "-std=c11", "-Wall", "-Wextra", "-Werror", str(generated), "-o", str(executable)],
                text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            return subprocess.run([str(executable)], text=True, capture_output=True, timeout=5, check=False)

    def assert_matches_reference(self, source):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-c-parity-") as temp:
            path = Path(temp) / "fixture.pusingcuk"
            path.write_text(source, encoding="utf-8")
            reference = subprocess.run(
                [sys.executable, str(ROOT / "pusingcuk_new.py"), str(path)],
                cwd=ROOT, text=True, capture_output=True, timeout=10, check=False,
            )
            compiled = self.compile_and_run(source)
            self.assertEqual(compiled.returncode, reference.returncode, reference.stderr)
            self.assertEqual(compiled.stdout, reference.stdout)
            if reference.returncode != 0:
                self.assertEqual(compiled.stdout, "")

    def test_compiles_and_runs_integer_arithmetic(self):
        result = self.compile_and_run(
            "jancuk\nlah angka = 6 * 7\nangka = angka + 1\nhedeh angka\nselesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "43\n")

    def test_floor_division_and_modulo_match_python_for_sign_combinations(self):
        source = (
            "jancuk\n"
            "hedeh -7 // 3\n"
            "hedeh -7 % 3\n"
            "hedeh 7 // -3\n"
            "hedeh 7 % -3\n"
            "hedeh -7 // -3\n"
            "hedeh -7 % -3\n"
            "hedeh 9223372036854775807 // 2\n"
            "hedeh 9223372036854775807 % 2\n"
            "selesai jancuk"
        )
        self.assert_matches_reference(source)
        result = self.compile_and_run(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "-3\n2\n-3\n-2\n2\n-1\n4611686018427387903\n1\n")

    def test_division_by_zero_matches_reference_failure(self):
        self.assert_matches_reference("jancuk\nhedeh 12 // 0\nselesai jancuk")
        result = self.compile_and_run("jancuk\nhedeh 12 // 0\nselesai jancuk")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("division by zero", result.stderr)

    def test_modulo_by_zero_matches_reference_failure(self):
        self.assert_matches_reference("jancuk\nhedeh -12 % 0\nselesai jancuk")
        result = self.compile_and_run("jancuk\nhedeh -12 % 0\nselesai jancuk")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("division by zero", result.stderr)

    def test_comparisons_booleans_and_short_circuit_match_reference(self):
        source = (
            "jancuk\n"
            "hedeh 2 < 3\n"
            "hedeh 3 == 3\n"
            "hedeh benar == 1\n"
            "hedeh bukan salah\n"
            "hedeh (2 < 3) dan (5 >= 5)\n"
            "hedeh salah dan (1 // 0 == 0)\n"
            "hedeh benar atau (1 // 0 == 0)\n"
            "selesai jancuk"
        )
        self.assert_matches_reference(source)
        result = self.compile_and_run(source)
        self.assertEqual(result.stdout, "okelah\nokelah\ntidak\nokelah\nokelah\ntidak\nokelah\n")

    def test_mixed_type_equality_still_evaluates_both_operands(self):
        # Type-sensitive equality must not optimize away a failing right operand.
        self.assert_matches_reference("jancuk\nhedeh benar == (1 // 0)\nselesai jancuk")

    def test_if_else_and_nested_boolean_condition_match_reference(self):
        source = (
            "jancuk\n"
            "lah skor = 7\n"
            "njir skor >= 5 dan benar\n"
            "    hedeh 42\n"
            "kampret\n"
            "    hedeh 0\n"
            "selesai njir\n"
            "njir skor < 5 atau salah\n"
            "    hedeh 0\n"
            "kampret\n"
            "    hedeh benar\n"
            "selesai njir\n"
            "selesai jancuk"
        )
        self.assert_matches_reference(source)
        result = self.compile_and_run(source)
        self.assertEqual(result.stdout, "42\nokelah\n")

    def test_condition_short_circuits_division_by_zero(self):
        source = (
            "jancuk\n"
            "njir salah dan (1 // 0 == 0)\n"
            "    hedeh 0\n"
            "kampret\n"
            "    hedeh 9\n"
            "selesai njir\n"
            "selesai jancuk"
        )
        self.assert_matches_reference(source)
        self.assertEqual(self.compile_and_run(source).stdout, "9\n")

    def test_rejects_variable_type_changes(self):
        source = "jancuk\nlah nilai = 1\nnilai = benar\nselesai jancuk"
        with self.assertRaisesRegex(CBackendError, "perubahan tipe"):
            generate(from_source(source))

    def test_detects_runtime_integer_overflow(self):
        result = self.compile_and_run(
            "jancuk\nlah angka = 9223372036854775807\n"
            "angka = angka + 1\nhedeh angka\nselesai jancuk"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("integer overflow", result.stderr)

    def test_rejects_unsupported_feature_instead_of_changing_semantics(self):
        with self.assertRaisesRegex(CBackendError, "literal integer"):
            generate(from_source('jancuk\nhedeh "halo"\nselesai jancuk'))

    def test_rejects_use_before_declaration(self):
        with self.assertRaisesRegex(CBackendError, "belum dideklarasikan"):
            generate(from_source("jancuk\nhedeh angka\nselesai jancuk"))


    def test_while_loop_matches_reference(self):
        source = (
            "jancuk\nlah i = 1\nlah total = 0\n"
            "mumet i <= 5\n"
            "    total = total + i\n"
            "    i = i + 1\n"
            "selesai mumet\nhedeh total\nselesai jancuk"
        )
        self.assert_matches_reference(source)
        self.assertEqual(self.compile_and_run(source).stdout, "15\n")

    def test_integer_functions_and_forward_calls_match_reference(self):
        source = (
            "jancuk\n"
            "hedeh tambah(20, 22)\n"
            "fungsi tambah(a, b)\n"
            "    balek a + b\n"
            "selesai fungsi\n"
            "selesai jancuk"
        )
        self.assert_matches_reference(source)
        self.assertEqual(self.compile_and_run(source).stdout, "42\n")

    def test_recursive_integer_function_matches_reference(self):
        source = (
            "jancuk\n"
            "fungsi faktorial(n)\n"
            "    njir n <= 1\n"
            "        balek 1\n"
            "    selesai njir\n"
            "    balek n * faktorial(n - 1)\n"
            "selesai fungsi\n"
            "hedeh faktorial(6)\n"
            "selesai jancuk"
        )
        self.assert_matches_reference(source)
        self.assertEqual(self.compile_and_run(source).stdout, "720\n")

    def test_loop_rejects_local_declarations_explicitly(self):
        source = "jancuk\nmumet salah\n    lah x = 1\nselesai mumet\nselesai jancuk"
        with self.assertRaisesRegex(CBackendError, "deklarasi lah di dalam loop"):
            generate(from_source(source))

    def test_function_requires_integer_arguments_and_return(self):
        with self.assertRaisesRegex(CBackendError, "parameter fungsi C subset harus integer"):
            generate(from_source("jancuk\nfungsi identitas(x)\n    balek x\nselesai fungsi\nhedeh identitas(benar)\nselesai jancuk"))


    def test_genz_aliases_work_across_loop_condition_and_function(self):
        source = (
            "gas\nbestie angka = 3\n"
            "fungsi kuadrat(n)\n    balek n * n\nselesai fungsi\n"
            "mumet angka > 0\n    spill kuadrat(angka)\n    angka = angka - 1\nselesai mumet\n"
            "njir valid\n    spill zonk\nskip\n    spill valid\nkelar njir\nkelar gas"
        )
        self.assert_matches_reference(source)
        self.assertEqual(self.compile_and_run(source).stdout, "9\n4\n1\ntidak\n")


if __name__ == "__main__":
    unittest.main()
