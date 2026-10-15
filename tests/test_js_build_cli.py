"""End-to-end tests for the user-facing JavaScript build command."""
from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from compiler.js_backend import main

NODE = shutil.which("node")


class JavaScriptBuildCommandTests(unittest.TestCase):
    def test_build_command_writes_runnable_artifact(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-build-") as temp:
            root = Path(temp)
            source = root / "hello.cuk"
            artifact = root / "hello.js"
            source.write_text(
                "jancuk\n"
                "lah angka = 40 + 2\n"
                "hedeh angka\n"
                "selesai jancuk\n",
                encoding="utf-8",
            )
            self.assertEqual(main([str(source), "--output", str(artifact)]), 0)
            self.assertTrue(artifact.is_file())
            self.assertIn("// Program utama", artifact.read_text(encoding="utf-8"))
            if NODE:
                result = subprocess.run(
                    [NODE, str(artifact)], text=True, capture_output=True,
                    timeout=10, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "42\n")

    def test_build_command_reports_missing_source(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-build-missing-") as temp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main([str(Path(temp) / "missing.cuk"), "--output", str(Path(temp) / "never-created.js")])
            self.assertEqual(result, 2)
            self.assertIn("berkas tidak ditemukan", stderr.getvalue())

    def test_build_command_rejects_unsupported_source_without_artifact(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-build-error-") as temp:
            root = Path(temp)
            source = root / "unsupported.cuk"
            artifact = root / "unsupported.js"
            source.write_text(
                "jancuk\n"
                "hedeh fungsi_yang_tidak_ada(1)\n"
                "selesai jancuk\n",
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main([str(source), "--output", str(artifact)])
            self.assertEqual(result, 1)
            self.assertIn("Kesalahan kompilasi JavaScript", stderr.getvalue())
            self.assertFalse(artifact.exists())


if __name__ == "__main__":
    unittest.main()
