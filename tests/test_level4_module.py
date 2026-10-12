import os
import tempfile
import unittest
from pathlib import Path

from evaluator import Evaluator, PusingDict


def source(body):
    return "jancuk\n" + body + "\nselesai jancuk\n"


def write_module(root, relative_path, body):
    path = Path(root) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source(body), encoding="utf-8")
    return path


class Level4ModuleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.main_file = self.root / "main.pusingcuk"
        self.main_file.write_text(source(""), encoding="utf-8")
        self.old_cwd = os.getcwd()
        self.other_cwd = tempfile.TemporaryDirectory()
        self.addCleanup(self.other_cwd.cleanup)
        os.chdir(self.other_cwd.name)
        self.addCleanup(os.chdir, self.old_cwd)

    def evaluator(self):
        return Evaluator(source_path=self.main_file, project_root=self.root)

    def test_angkut_relative_path_uses_caller_file_not_cwd(self):
        write_module(self.root, "lib/parent.pusingcuk",
                     'lah child = angkut("child.pusingcuk")')
        write_module(self.root, "lib/child.pusingcuk",
                     'lah marker = "from-caller-directory"')
        env = self.evaluator().run_module(source(
            'lah mod = angkut("lib/parent.pusingcuk")'
        ))
        mod = env["mod"]
        self.assertIsInstance(mod, PusingDict)
        self.assertEqual(mod["child"]["marker"], "from-caller-directory")

    def test_angkut_cycle_detection(self):
        write_module(self.root, "a.pusingcuk",
                     'lah b = angkut("b.pusingcuk")')
        write_module(self.root, "b.pusingcuk",
                     'lah a = angkut("a.pusingcuk")')
        env = self.evaluator().run_module(source(
            'lah a = angkut("a.pusingcuk")'
        ))
        self.assertIsInstance(env["a"], PusingDict)
        self.assertIsInstance(env["a"]["b"], PusingDict)
        self.assertIs(env["a"]["b"]["a"], False)
        self.assertEqual(self.evaluator()._module_loading_stack, set())

    def test_angkut_cache_returns_same_object(self):
        write_module(self.root, "cached.pusingcuk", 'lah value = 7')
        env = self.evaluator().run_module(source(
            'lah first = angkut("cached.pusingcuk")\n'
            'lah second = angkut("cached.pusingcuk")'
        ))
        self.assertIs(env["first"], env["second"])

    def test_angkut_reject_outside_repo(self):
        env = self.evaluator().run_module(source(
            'lah outside = angkut("../../etc/passwd")'
        ))
        self.assertIs(env["outside"], False)

    def test_angkut_reject_non_pusingcuk_extension(self):
        (self.root / "not-a-module.txt").write_text("secret", encoding="utf-8")
        env = self.evaluator().run_module(source(
            'lah invalid = angkut("not-a-module.txt")'
        ))
        self.assertIs(env["invalid"], False)

    def test_angkut_reject_absolute_path_and_large_file(self):
        env = self.evaluator().run_module(source(
            'lah absolute = angkut("/etc/passwd")'
        ))
        self.assertIs(env["absolute"], False)
        (self.root / "large.pusingcuk").write_bytes(b"x" * (1024 * 1024 + 1))
        env = self.evaluator().run_module(source(
            'lah large = angkut("large.pusingcuk")'
        ))
        self.assertIs(env["large"], False)


if __name__ == "__main__":
    unittest.main()
