"""Regression checks for generated PVM filesystem guards."""
import os
import tempfile
import unittest
from pathlib import Path

from src.backends.python.compiler import compile_pvm


class PvmPathSandboxTests(unittest.TestCase):
    def make_python_runtime(self, cwd):
        generated = compile_pvm([(11, "'safe.txt'")])
        old_cwd = Path.cwd()
        try:
            os.chdir(cwd)
            namespace = {"__name__": "pvm_runtime_test"}
            exec(compile(generated, "<generated-pvm>", "exec"), namespace)
            return namespace
        finally:
            os.chdir(old_cwd)

    def test_python_runtime_accepts_project_relative_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = self.make_python_runtime(temporary)
            self.assertEqual(runtime["__safe_path"]("nested.txt"), Path(temporary) / "nested.txt")

    def test_python_runtime_rejects_parent_and_absolute_paths(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.NamedTemporaryFile() as outside:
            runtime = self.make_python_runtime(temporary)
            for candidate in ("../secret.txt", outside.name, "nested/../../secret.txt"):
                with self.subTest(candidate=candidate):
                    with self.assertRaises(ValueError):
                        runtime["__safe_path"](candidate)

    def test_python_runtime_rejects_symlink_components(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root, link = Path(temporary), Path(temporary) / "link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not supported on this platform")
            runtime = self.make_python_runtime(temporary)
            with self.assertRaises(ValueError):
                runtime["__safe_path"]("link/secret.txt")

    def test_javascript_runtime_wraps_file_opcodes(self):
        source = (Path(__file__).resolve().parents[1] / "src" / "backends" / "js" / "compiler.js").read_text(encoding="utf-8")
        self.assertIn("function __safePath(value)", source)
        self.assertIn("fs.openSync(__safePath(", source)
        self.assertIn("fs.readFileSync(__safePath(", source)
        self.assertIn("fs.rmSync(__safePath(", source)


if __name__ == "__main__":
    unittest.main()
