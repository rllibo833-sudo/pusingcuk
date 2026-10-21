"""Compatibility tests for compiler targets consumed by the conformance runners."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CompilerTargetCompatibilityTests(unittest.TestCase):
    def test_go_target_generates_standalone_go_source(self) -> None:
        source_text = 'jancuk\nhedeh "halo PusingCuk"\nselesai jancuk\n'
        with tempfile.TemporaryDirectory(prefix="pusingcuk-go-target-") as directory:
            directory_path = Path(directory)
            source = directory_path / "hello.cuk"
            output = directory_path / "hello.go"
            source.write_text(source_text, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable, "-m", "compiler", str(source),
                    "--target", "go", "--output", str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(output.is_file())
            generated = output.read_text(encoding="utf-8")
            self.assertIn("package main", generated)
            self.assertIn("halo PusingCuk", generated)


if __name__ == "__main__":
    unittest.main()
