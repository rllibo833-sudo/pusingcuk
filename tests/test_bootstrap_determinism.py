"""End-to-end determinism check for the current Python-IR -> C backend path.

This deliberately does not claim self-hosting: parsing and IR generation still
run on Python. It verifies repeatable C emission and equivalent native execution.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C_COMPILER = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")


@unittest.skipUnless(C_COMPILER, "C11 compiler tidak tersedia")
class BootstrapDeterminismTests(unittest.TestCase):
    def test_ir_to_c_emission_is_repeatable_and_native_output_matches(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-bootstrap-proof-") as tmp:
            work = Path(tmp)
            source = ROOT / "examples" / "hello.cuk"
            ir_file = work / "hello.ir.json"
            c_files = [work / "stage1-a.c", work / "stage1-b.c"]
            binaries = [work / "stage1-a", work / "stage1-b"]

            parsed = subprocess.run(
                [sys.executable, "-m", "compiler.ir", str(source), "-o", str(ir_file)],
                cwd=ROOT, text=True, capture_output=True, timeout=15, check=False,
            )
            self.assertEqual(parsed.returncode, 0, parsed.stderr)
            ir_bytes = ir_file.read_bytes()

            for c_file in c_files:
                generated = subprocess.run(
                    [sys.executable, "-m", "compiler.c_backend", "--ir", str(ir_file), "-o", str(c_file)],
                    cwd=ROOT, text=True, capture_output=True, timeout=15, check=False,
                )
                self.assertEqual(generated.returncode, 0, generated.stderr)

            self.assertEqual(c_files[0].read_bytes(), c_files[1].read_bytes(),
                             "C backend emitted different source for the same validated IR")

            outputs = []
            for c_file, binary in zip(c_files, binaries):
                built = subprocess.run(
                    [C_COMPILER, "-std=c11", "-Wall", "-Wextra", "-Werror",
                     str(c_file), "-o", str(binary)],
                    cwd=ROOT, text=True, capture_output=True, timeout=30, check=False,
                )
                self.assertEqual(built.returncode, 0, built.stderr)
                ran = subprocess.run(
                    [str(binary)], cwd=ROOT, text=True, capture_output=True,
                    timeout=5, check=False,
                )
                self.assertEqual(ran.returncode, 0, ran.stderr)
                outputs.append(ran.stdout)

            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(outputs[0], "Halo, Dunia\\n")
            self.assertTrue(ir_bytes, "Python frontend produced an empty IR artifact")


if __name__ == "__main__":
    unittest.main()
