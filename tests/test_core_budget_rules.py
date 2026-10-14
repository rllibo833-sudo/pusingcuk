"""Regression tests for pure business rules intended for CORE CI integration."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"
FIXTURE = ROOT / "examples" / "core" / "anggaran_sufficiency.cuk"


class CoreBudgetRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native_dir = tempfile.TemporaryDirectory(prefix="pusingcuk-core-budget-")
        cls.native_cli = Path(cls.native_dir.name) / "pusingcuk-native"
        build = subprocess.run(
            ["make", "native", f"NATIVE_BIN={cls.native_cli}"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        if build.returncode != 0:
            raise RuntimeError(f"native runtime build failed: {build.stdout}\n{build.stderr}")

    @classmethod
    def tearDownClass(cls):
        cls.native_dir.cleanup()

    def test_budget_sufficiency_same_fixture_reference_and_native(self):
        fixture_path = ROOT / "tests" / "fixtures" / "core_budget_sufficiency.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual(fixture["schema_version"], 1)
        self.assertEqual(fixture["rule_id"], "budget.sufficiency.v1")
        self.assertEqual(fixture["source_commit"], "411c532454028d2d5e733373d085050eca1d402a")
        source = ROOT / fixture["source_path"]
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(),
            fixture["source_sha256"],
            "registered .cuk source hash changed; update its pin only through reviewed synchronization",
        )
        self.assertGreaterEqual(len(fixture["cases"]), 6)
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                stdin = "".join(f"{value}\n" for value in case["input"])
                reference = subprocess.run(
                    [sys.executable, str(ROOT / "pusingcuk_new.py"), str(source)],
                    cwd=ROOT, input=stdin, text=True, capture_output=True, timeout=5, check=False,
                )
                native = subprocess.run(
                    [str(self.native_cli), str(source)],
                    cwd=ROOT, input=stdin, text=True, capture_output=True, timeout=5, check=False,
                )
                expected = case["expected"] + "\n"
                self.assertEqual(reference.returncode, 0, reference.stderr)
                self.assertEqual(native.returncode, 0, native.stderr)
                self.assertEqual(reference.stdout, expected)
                self.assertEqual(native.stdout, expected)
                self.assertEqual(reference.stdout, native.stdout)
                self.assertEqual(reference.stderr, "")
                self.assertEqual(native.stderr, "")

    def test_budget_sufficiency_reference_fixture(self):
        result = subprocess.run(
            [sys.executable, str(CLI), str(FIXTURE)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "SALDO_CUKUP\n"
            "SALDO_CUKUP\n"
            "SALDO_TIDAK_CUKUP\n"
            "SALDO_CUKUP\n"
            "INPUT_TIDAK_VALID\n"
            "INPUT_TIDAK_VALID\n",
        )
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
