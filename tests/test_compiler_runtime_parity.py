"""Cross-backend runtime diagnostics and newly mapped Python builtins."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.bytecode import compile_ir
from compiler.ir import from_source
from compiler.js_backend import generate as generate_js
from compiler.python_backend import generate as generate_python

ROOT = Path(__file__).resolve().parents[1]
DIVISION_BY_ZERO = """jancuk
hedeh 5 / 0
selesai jancuk
"""


class CompilerRuntimeParityTests(unittest.TestCase):
    def test_python_transpiler_emits_canonical_runtime_error(self):
        generated = generate_python(from_source(DIVISION_BY_ZERO))
        result = subprocess.run(
            [sys.executable, "-c", generated], cwd=ROOT,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Kesalahan runtime: Baris 2:", result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
    def test_javascript_emits_canonical_runtime_error(self):
        generated = generate_js(from_source(DIVISION_BY_ZERO))
        result = subprocess.run(
            [shutil.which("node"), "-e", generated], cwd=ROOT,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Kesalahan runtime: Baris 2:", result.stderr)

    def test_vm_emits_canonical_runtime_error(self):
        document = compile_ir(from_source(DIVISION_BY_ZERO))
        with tempfile.TemporaryDirectory() as tmp:
            bytecode = Path(tmp) / "division-zero.json"
            bytecode.write_text(json.dumps(document), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "compiler.vm", str(bytecode)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Kesalahan runtime: Baris 2:", result.stderr)

    def test_python_transpiler_supports_sum_and_logarithms(self):
        source = """jancuk
hedeh jumlah([1, 2, 3])
hedeh logaritma(1)
hedeh log10(100)
selesai jancuk
"""
        generated = generate_python(from_source(source))
        result = subprocess.run(
            [sys.executable, "-c", generated], cwd=ROOT,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "6\n0\n2\n")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
