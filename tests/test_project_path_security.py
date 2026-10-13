"""Regression tests for project-root filesystem confinement."""
import tempfile
import unittest
from pathlib import Path
from evaluator import _confined_project_path, _read_project_text, capture


class ProjectPathSecurityTests(unittest.TestCase):
    def test_accepts_relative_path_inside_project(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "nested").mkdir()
            self.assertEqual(_confined_project_path(root, "nested/program.cuk"), root / "nested/program.cuk")

    def test_rejects_parent_traversal_and_absolute_paths(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.NamedTemporaryFile() as outside:
            for candidate in ("../secret.txt", "nested/../../secret.txt", r"sub\..\secret.txt", outside.name):
                with self.subTest(candidate=candidate):
                    with self.assertRaises(ValueError):
                        _confined_project_path(temporary, candidate)

    def test_rejects_symlink_components_for_resolve_and_read(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root, link = Path(temporary), Path(temporary) / "link"
            (Path(outside) / "secret.txt").write_text("secret", encoding="utf-8")
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not supported on this platform")
            with self.assertRaises(ValueError):
                _confined_project_path(root, "link/secret.txt")
            with self.assertRaises((OSError, ValueError)):
                _read_project_text(root, "link/secret.txt")

    def test_language_file_builtins_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary)
            outside_file = Path(outside) / "secret.txt"
            outside_file.write_text("secret", encoding="utf-8")
            source = (
                'jancuk\n'
                'hedeh tulis("../secret.txt", "modified")\n'
                'hedeh baca("' + str(outside_file).replace("\\", "\\\\") + '")\n'
                'selesai jancuk'
            )
            output = capture(source, source_path=root / "main.cuk", project_root=root)
            self.assertEqual(output, "tidak\ntidak\n")
            self.assertEqual(outside_file.read_text(encoding="utf-8"), "secret")


if __name__ == "__main__":
    unittest.main()
