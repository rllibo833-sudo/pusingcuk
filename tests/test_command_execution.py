import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluator import capture, _execute_command
from parser import parse


class CommandExecutionTests(unittest.TestCase):
    def test_execution_is_disabled_without_explicit_opt_in(self):
        with patch.dict(os.environ, {}, clear=True):
            result = capture('jancuk\nhedeh eksekusi("free -m")\nselesai jancuk')
        self.assertIn("dinonaktifkan", result)

    def test_allowlisted_command_runs_without_a_shell(self):
        completed = subprocess.CompletedProcess(["/usr/bin/free", "-m"], 0, "Mem: 1 2 3\n", "")
        with patch.dict(os.environ, {"PUSINGCUK_ENABLE_EXECUTION": "1"}), \
             patch("evaluator.shutil.which", return_value="/usr/bin/free"), \
             patch("evaluator.subprocess.run", return_value=completed) as run:
            result = capture('jancuk\nhedeh eksekusi("free -m")\nselesai jancuk')
        self.assertEqual(result, "Mem: 1 2 3\n")
        self.assertEqual(run.call_args.args[0], ["/usr/bin/free", "-m"])
        self.assertIs(run.call_args.kwargs["shell"], False)
        self.assertEqual(run.call_args.kwargs["timeout"], 30)

    def test_shell_chaining_and_unknown_commands_are_rejected(self):
        with patch.dict(os.environ, {"PUSINGCUK_ENABLE_EXECUTION": "1"}), \
             patch("evaluator.subprocess.run") as run:
            chained = _execute_command("df -h /data && free -m", ".")
            unknown = _execute_command("echo hello", ".")
        self.assertIn("tidak ada dalam daftar izin", chained)
        self.assertIn("tidak ada dalam daftar izin", unknown)
        run.assert_not_called()

    def test_remote_examples_parse_with_the_reference_parser(self):
        root = Path(__file__).resolve().parents[1]
        for relative in (
            "examples/remote/gemini_agent.cuk",
            "examples/remote/bot_termux.cuk",
        ):
            with self.subTest(path=relative):
                parse((root / relative).read_text(encoding="utf-8"), filename=relative)


if __name__ == "__main__":
    unittest.main()
