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


if __name__ == "__main__":
    unittest.main()
