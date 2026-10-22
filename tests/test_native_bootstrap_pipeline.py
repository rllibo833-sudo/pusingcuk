"""A native-only seed -> .cuk codegen -> native bytecode execution path."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEGEN = ROOT / "examples" / "self_hosting" / "ir_codegen.cuk"


class NativeBootstrapPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = next((shutil.which(name) for name in ("cc", "gcc", "clang") if shutil.which(name)), None)
        if compiler is None:
            raise unittest.SkipTest("native C compiler is not installed")
        cls.tmp = tempfile.TemporaryDirectory(prefix="pusingcuk-bootstrap-")
        cls.directory = Path(cls.tmp.name)
        cls.native = cls.directory / "pusingcuk-native"
        cls.seed = cls.directory / "pusingcuk-bootstrap"
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-Wall", "-Wextra",
             str(ROOT / "native" / "pusingcuk.c"), "-lm", "-o", str(cls.native)],
            cwd=ROOT, check=True, capture_output=True, text=True, timeout=90,
        )
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-Wall", "-Wextra",
             str(ROOT / "native" / "pusingcuk_bootstrap.c"),
             str(ROOT / "native" / "cuk_lexer.c"),
             str(ROOT / "native" / "cuk_parser.c"),
             str(ROOT / "native" / "cuk_ir.c"),
             "-o", str(cls.seed)],
            cwd=ROOT, check=True, capture_output=True, text=True, timeout=90,
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_native_file_builtins_handle_large_text_and_collections(self):
        compiler_source = (ROOT / "examples" / "self_hosting" / "compiler.cuk").read_text(encoding="utf-8")
        large_json = ROOT / ".pusingcuk-native-large-input.json"
        large_text_out = ROOT / ".pusingcuk-native-large-text.txt"
        large_json_out = ROOT / ".pusingcuk-native-large-output.json"
        driver = self.directory / "file_builtins.cuk"
        payload = {"items": list(range(400))}
        large_json.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        driver.write_text(
            "jancuk\n"
            'lah source = baca_file("examples/self_hosting/compiler.cuk")\n'
            "hedeh panjang(source)\n"
            'lah data = baca_json(".pusingcuk-native-large-input.json")\n'
            'hedeh panjang(data["items"])\n'
            'lah wrote_text = tulis_file(".pusingcuk-native-large-text.txt", source)\n'
            "hedeh wrote_text\n"
            'lah wrote_json = tulis_json(".pusingcuk-native-large-output.json", data)\n'
            "hedeh wrote_json\n"
            "selesai jancuk\n",
            encoding="utf-8",
        )
        try:
            result = subprocess.run(
                [str(self.native), str(driver)], cwd=ROOT,
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.splitlines(), [str(len(compiler_source)), "400", "okelah", "okelah"])
            self.assertEqual(large_text_out.read_text(encoding="utf-8"), compiler_source)
            self.assertEqual(json.loads(large_json_out.read_text(encoding="utf-8")), payload)
        finally:
            for path in (large_json, large_text_out, large_json_out):
                path.unlink(missing_ok=True)

    def test_native_seed_codegen_and_vm_run_without_python_compiler(self):
        source = self.directory / "hello.cuk"
        source.write_text("jancuk\nhedeh 42\nselesai jancuk\n", encoding="utf-8")
        stage_zero = subprocess.run(
            [str(self.seed), str(source)], cwd=ROOT,
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(stage_zero.returncode, 0, stage_zero.stderr)
        ir = json.loads(stage_zero.stdout)
        self.assertEqual(ir["format"], "pusingcuk-ir")
        self.assertEqual(ir["program"]["kind"], "Program")

        codegen = subprocess.run(
            [str(self.native), str(CODEGEN)], cwd=ROOT,
            input=stage_zero.stdout, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(codegen.returncode, 0, codegen.stderr)
        self.assertFalse(codegen.stdout.startswith("BYTECODE_ERROR:"), codegen.stdout)
        bytecode = json.loads(codegen.stdout)
        self.assertEqual(bytecode["format"], "pusingcuk-bytecode")
        self.assertEqual(bytecode["code"][0][0], "CONST")

        bytecode_file = self.directory / "hello.bytecode.json"
        bytecode_file.write_text(codegen.stdout, encoding="utf-8")
        execution = subprocess.run(
            [str(self.native), "--run-bytecode", str(bytecode_file)],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(execution.returncode, 0, execution.stderr)
        self.assertEqual(execution.stdout, "42\n")


if __name__ == "__main__":
    unittest.main()
