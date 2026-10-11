import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from compiler.c_backend import CBackendError, generate
from compiler.ir import from_source


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
                [COMPILER, "-std=c11", "-Wall", "-Wextra", str(generated), "-o", str(executable)],
                text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            return subprocess.run([str(executable)], text=True, capture_output=True, timeout=5, check=False)

    def test_compiles_and_runs_integer_arithmetic(self):
        result = self.compile_and_run(
            "jancuk\nlah angka = 6 * 7\nangka = angka + 1\nhedeh angka\nselesai jancuk"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "43\n")

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
