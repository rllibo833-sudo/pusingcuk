"""Regression tests for default-deny PVM file capabilities and race-safe path access."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.backends.python.compiler import compile_pvm


class PvmPathSandboxTests(unittest.TestCase):
    def make_python_runtime(self, cwd, allow_file_io=False):
        generated = compile_pvm([(11, "'safe.txt'")])
        old_cwd = Path.cwd()
        argv = ["generated-pvm.py"] + (["--allow-file-io"] if allow_file_io else [])
        try:
            os.chdir(cwd)
            with patch("sys.argv", argv):
                namespace = {"__name__": "pvm_runtime_test"}
                exec(compile(generated, "<generated-pvm>", "exec"), namespace)
            self.addCleanup(self.close_runtime, namespace)
            return namespace
        finally:
            os.chdir(old_cwd)

    @staticmethod
    def close_runtime(runtime):
        fd = runtime.get("__pvm_root_fd")
        if fd is not None:
            os.close(fd)
            runtime["__pvm_root_fd"] = None

    def open_write(self, runtime, path, data=b"safe"):
        flags = runtime["os"].O_WRONLY | runtime["os"].O_CREAT | runtime["os"].O_TRUNC
        fd = runtime["__open_beneath"](path, flags)
        try:
            runtime["os"].write(fd, data)
        finally:
            runtime["os"].close(fd)

    def test_python_file_ops_are_disabled_without_explicit_capability(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = self.make_python_runtime(temporary)
            with self.assertRaisesRegex(PermissionError, "dinonaktifkan"):
                runtime["__read_beneath"]("safe.txt")

    def test_python_runtime_reads_and_writes_relative_file_with_capability(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = self.make_python_runtime(temporary, allow_file_io=True)
            self.open_write(runtime, "safe.txt", b"relative")
            self.assertEqual(runtime["__read_beneath"]("safe.txt"), "relative")

    def test_python_runtime_rejects_parent_and_absolute_paths(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.NamedTemporaryFile() as outside:
            runtime = self.make_python_runtime(temporary, allow_file_io=True)
            flags = runtime["os"].O_RDONLY
            for candidate in ("../secret.txt", outside.name, "nested/../../secret.txt", "C:\\secret.txt"):
                with self.subTest(candidate=candidate):
                    with self.assertRaises(ValueError):
                        runtime["__open_beneath"](candidate, flags)

    def test_python_runtime_rejects_symlink_directory_and_final_file(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary)
            outside_file = Path(outside) / "secret.txt"
            outside_file.write_text("secret", encoding="utf-8")
            try:
                (root / "linkdir").symlink_to(outside, target_is_directory=True)
                (root / "linkfile").symlink_to(outside_file)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not supported on this platform")
            runtime = self.make_python_runtime(temporary, allow_file_io=True)
            with self.assertRaises(PermissionError):
                runtime["__read_beneath"]("linkdir/secret.txt")
            with self.assertRaises(PermissionError):
                runtime["__read_beneath"]("linkfile")
            self.assertEqual(outside_file.read_text(encoding="utf-8"), "secret")

    def test_runtime_root_is_pinned_when_process_changes_cwd(self):
        with tempfile.TemporaryDirectory() as project, tempfile.TemporaryDirectory() as other:
            runtime = self.make_python_runtime(project, allow_file_io=True)
            original = Path.cwd()
            try:
                os.chdir(other)
                self.open_write(runtime, "anchored.txt", b"project")
            finally:
                os.chdir(original)
            self.assertEqual((Path(project) / "anchored.txt").read_bytes(), b"project")
            self.assertFalse((Path(other) / "anchored.txt").exists())

    def test_python_delete_rejects_symlinks_and_stays_beneath_root(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary)
            target = Path(outside) / "keep.txt"
            target.write_text("keep", encoding="utf-8")
            link = root / "link.txt"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not supported on this platform")
            runtime = self.make_python_runtime(temporary, allow_file_io=True)
            with self.assertRaises(PermissionError):
                runtime["__unlink_beneath"]("link.txt")
            self.assertEqual(target.read_text(encoding="utf-8"), "keep")
            self.open_write(runtime, "remove.txt")
            runtime["__unlink_beneath"]("remove.txt")
            self.assertFalse((root / "remove.txt").exists())

    def test_javascript_backend_disables_all_file_opcodes(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "backends" / "js" / "compiler.js"
        ).read_text(encoding="utf-8")
        self.assertIn("PVM JavaScript backend menonaktifkan opcode file", source)
        self.assertNotIn("fs.openSync(__safePath(", source)
        self.assertNotIn("fs.readFileSync(__safePath(", source)
        self.assertNotIn("fs.rmSync(__safePath(", source)


if __name__ == "__main__":
    unittest.main()
