"""Regression tests for deterministic, bounded, portable registered .cuk rules."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "priority_triage.json"


class RegisteredRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.source = (ROOT / cls.fixture["source_path"]).resolve()
        cls.source.relative_to(ROOT)
        cls.source_text = cls.source.read_text(encoding="utf-8")

    def test_manifest_is_bounded_and_source_hash_is_pinned(self):
        fixture = self.fixture
        self.assertEqual(fixture["schema_version"], 1)
        self.assertEqual(fixture["rule_id"], "operations.priority-triage.v1")
        self.assertEqual(len(fixture["cases"]), 12)
        self.assertEqual(len({case["id"] for case in fixture["cases"]}), 12)
        self.assertEqual(
            hashlib.sha256(self.source_text.encode("utf-8")).hexdigest(),
            fixture["source_sha256"],
        )
        self.assertEqual(
            [field["name"] for field in fixture["input_contract"]],
            ["urgensi", "dampak"],
        )

    def test_invalid_fixture_inputs_are_not_silently_marked_valid(self):
        for case in self.fixture["cases"]:
            values = case["input"]
            self.assertEqual(len(values), 2, case["id"])
            self.assertTrue(all(isinstance(v, int) and not isinstance(v, bool) for v in values), case["id"])
            in_range = all(1 <= value <= 5 for value in values)
            if not in_range:
                self.assertEqual(case["expected"], "INPUT_TIDAK_VALID", case["id"])

    def test_native_runtime_matches_reference_for_all_rule_cases(self):
        compiler = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
        if compiler is None:
            self.skipTest("compiler C tidak tersedia; CI native wajib menjalankan tes native terpisah")

        with tempfile.TemporaryDirectory(prefix="pusingcuk-rule-parity-") as directory:
            native_bin = Path(directory) / "pusingcuk-native"
            build = subprocess.run(
                [
                    compiler, "-std=c11", "-O2", "-Wall", "-Wextra",
                    '-DPUSINGCUK_VERSION="conformance"',
                    str(ROOT / "native" / "pusingcuk.c"), "-lm", "-o", str(native_bin),
                ],
                text=True,
                encoding="utf-8",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                cwd=ROOT,
                check=False,
            )
            self.assertEqual(build.returncode, 0, build.stderr)

            reference = [sys.executable, str(ROOT / "pusingcuk_new.py"), str(self.source)]
            native = [str(native_bin), str(self.source)]
            for case in self.fixture["cases"]:
                stdin_text = f"{case['input'][0]}\\n{case['input'][1]}\\n"
                with self.subTest(case=case["id"]):
                    reference_result = subprocess.run(
                        reference, input=stdin_text, text=True, encoding="utf-8",
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5,
                        cwd=ROOT, check=False,
                    )
                    native_result = subprocess.run(
                        native, input=stdin_text, text=True, encoding="utf-8",
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5,
                        cwd=ROOT, check=False,
                    )
                    self.assertEqual(native_result.returncode, reference_result.returncode)
                    self.assertEqual(native_result.stdout, reference_result.stdout)
                    self.assertEqual(native_result.stdout, case["expected"] + "\\n")
                    self.assertEqual(native_result.stderr == "", reference_result.stderr == "")

    def test_reference_runtime_matches_all_rule_cases(self):
        command = [sys.executable, str(ROOT / "pusingcuk_new.py"), str(self.source)]
        for case in self.fixture["cases"]:
            with self.subTest(case=case["id"]):
                completed = subprocess.run(
                    command,
                    input=f"{case['input'][0]}\n{case['input'][1]}\n",
                    text=True,
                    encoding="utf-8",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5,
                    cwd=ROOT,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stdout, case["expected"] + "\n")


if __name__ == "__main__":
    unittest.main()
