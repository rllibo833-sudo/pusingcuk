"""End-to-end parity tests for the .cuk IR v1 bytecode generator."""
from __future__ import annotations
import json
import subprocess
import sys
import unittest
from pathlib import Path
from compiler.bytecode import compile_ir
from compiler.ir import from_source

ROOT = Path(__file__).resolve().parents[1]
CODEGEN = ROOT / "examples" / "self_hosting" / "ir_codegen.cuk"

def program(*lines):
    return chr(10).join(("jancuk", *lines, "selesai jancuk", ""))

class IRCukCodegenParityTests(unittest.TestCase):
    def run_codegen(self, ir):
        payload = json.dumps(ir, ensure_ascii=False, separators=(",", ":"))
        self.assertLessEqual(len(payload.encode()), 1023, "IR exceeds json_baca builtin limit")
        result = subprocess.run(
            [sys.executable, str(ROOT / "pusingcuk_new.py"), str(CODEGEN)],
            cwd=ROOT, input=payload + chr(10), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(result.stdout.startswith("BYTECODE_ERROR:"), result.stdout)
        output = result.stdout.strip()
        self.assertLessEqual(len(output.encode()), 1023, "bytecode exceeds json_teks builtin limit")
        actual = json.loads(output)
        self.assertEqual(actual["format"], "pusingcuk-bytecode")
        self.assertEqual(actual["bytecode_version"], 1)
        return actual

    def test_ir_to_bytecode_matches_python_reference(self):
        sources = (
            program("hedeh 7"),
            program("lah x = 2 + 3", "hedeh x"),
            program("mumet salah", "    hedeh 1", "selesai mumet"),
            program("untuk x dalam [1]", "    hedeh x", "selesai untuk"),
            program("fungsi f(x)", "    balek x", "selesai fungsi", "hedeh f(2)"),
        )
        for index, source in enumerate(sources):
            with self.subTest(source=index):
                ir = from_source(source, "probe.cuk")
                self.assertEqual(self.run_codegen(ir), compile_ir(ir))

    def test_try_is_rejected_without_fallback(self):
        ir = from_source(program("hedeh 1"), "reject.cuk")
        ir["program"]["fields"]["body"] = [{
            "kind": "Try", "line": 1,
            "fields": {"body": [], "handler_name": None, "handler": [], "final": []},
        }]
        result = subprocess.run(
            [sys.executable, str(ROOT / "pusingcuk_new.py"), str(CODEGEN)],
            cwd=ROOT, input=json.dumps(ir, separators=(",", ":")) + chr(10),
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("BYTECODE_ERROR:", result.stdout)
        self.assertIn("Try", result.stdout)

    def test_return_outside_function_is_rejected(self):
        ir = from_source(program("hedeh 1"), "reject.cuk")
        ir["program"]["fields"]["body"] = [{
            "kind": "Return", "line": 1, "fields": {"value": None},
        }]
        result = subprocess.run(
            [sys.executable, str(ROOT / "pusingcuk_new.py"), str(CODEGEN)],
            cwd=ROOT, input=json.dumps(ir, separators=(",", ":")) + chr(10),
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("BYTECODE_ERROR:", result.stdout)
        self.assertIn("balek hanya boleh di dalam fungsi", result.stdout)

if __name__ == "__main__":
    unittest.main()
