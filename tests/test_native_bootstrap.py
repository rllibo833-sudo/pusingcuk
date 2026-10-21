"""Integration test for the standalone C frontend/bootstrap IR emitter."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CC = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")


@unittest.skipUnless(CC, "C compiler unavailable")
class NativeBootstrapTests(unittest.TestCase):
    def test_native_frontend_emits_valid_ir_v1_without_python_frontend(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-native-bootstrap-") as tmp:
            tmp = Path(tmp)
            binary = tmp / "pusingcuk_bootstrap"
            built = subprocess.run(
                [CC, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                 "-Wno-misleading-indentation",
                 "native/pusingcuk_bootstrap.c", "native/cuk_lexer.c",
                 "native/cuk_parser.c", "native/cuk_ir.c", "-o", str(binary)],
                cwd=ROOT, text=True, capture_output=True, timeout=30,
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            source = tmp / "hello.cuk"
            source.write_text(
                'jancuk\nlah nama = "Dunia"\nhedeh "Halo, " + nama\nselesai jancuk\n',
                encoding="utf-8",
            )
            emitted = subprocess.run(
                [str(binary), str(source)], cwd=ROOT, text=True, capture_output=True, timeout=5,
            )
            self.assertEqual(emitted.returncode, 0, emitted.stderr)
            document = json.loads(emitted.stdout)
            self.assertEqual(document["format"], "pusingcuk-ir")
            self.assertEqual(document["ir_version"], 1)
            self.assertEqual(document["source_name"], "hello.cuk")
            self.assertEqual(document["features"], ["console-output", "core", "operators", "variables"])
            self.assertEqual(document["program"]["kind"], "Program")
            self.assertEqual(document["program"]["fields"]["body"][1]["kind"], "Print")
            from compiler.ir import validate
            validate(document)

    def test_native_frontend_rejects_unsupported_syntax_closed(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-native-bootstrap-") as tmp:
            tmp = Path(tmp)
            binary = tmp / "pusingcuk_bootstrap"
            built = subprocess.run(
                [CC, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                 "-Wno-misleading-indentation",
                 "native/pusingcuk_bootstrap.c", "native/cuk_lexer.c",
                 "native/cuk_parser.c", "native/cuk_ir.c", "-o", str(binary)],
                cwd=ROOT, text=True, capture_output=True, timeout=30,
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            source = tmp / "unsupported.cuk"
            source.write_text("jancuk\nhedeh 1 * 2\nselesai jancuk\n", encoding="utf-8")
            emitted = subprocess.run(
                [str(binary), str(source)], cwd=ROOT, text=True, capture_output=True, timeout=5,
            )
            self.assertNotEqual(emitted.returncode, 0)
            self.assertEqual(emitted.stdout, "")


if __name__ == "__main__":
    unittest.main()
