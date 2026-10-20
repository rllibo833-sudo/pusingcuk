"""Fail-closed tests for the Cuk Reality Engine proposal gate."""
import json
from pathlib import Path
import sys
import unittest
from tools.reality_engine import REQUIRED_TARGETS, _run_command, validate_deterministic

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "tests" / "conformance" / "manifest.json").read_text(encoding="utf-8"))
FIXTURE = next(item for item in MANIFEST["fixtures"] if item["id"] == "core.output-arithmetic")
SOURCE = (ROOT / "tests" / "conformance" / FIXTURE["source"]).read_text(encoding="utf-8")
EXPECTED = FIXTURE["expected"]["stdout"]

def clean_evidence(source):
    return {
        "targets": {name: {"status": "PASS", "matched": True, "exit_code": 0, "stdout": EXPECTED, "stderr": ""}
                    for name in REQUIRED_TARGETS},
        "fixture_added": True, "fixture_id": FIXTURE["id"], "differential_ok": True, "regressions": [],
    }

class RealityEngineGateTests(unittest.TestCase):
    def test_nondeterministic_proposal_is_rejected_before_targets(self):
        called = []
        source = 'jancuk\nhedeh jam()\nselesai jancuk'
        result = validate_deterministic(source, target_runner=lambda text: called.append(text) or clean_evidence(text))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["diagnostic"][0]["code"], "NON_DETERMINISTIC")
        self.assertEqual(called, [])

    def test_unregistered_fixture_id_is_rejected(self):
        evidence = clean_evidence(SOURCE)
        evidence["fixture_id"] = "test-regression-1"
        result = validate_deterministic(SOURCE, target_runner=lambda _: evidence)
        self.assertFalse(result["accepted"])
        self.assertIn("FIXTURE_REQUIRED", {item["code"] for item in result["diagnostic"]})

    def test_fixture_source_must_match_manifest(self):
        source = 'jancuk\nhedeh "different"\nselesai jancuk'
        result = validate_deterministic(source, target_runner=lambda _: clean_evidence(SOURCE))
        self.assertFalse(result["accepted"])
        self.assertIn("FIXTURE_REQUIRED", {item["code"] for item in result["diagnostic"]})

    def test_any_backend_failure_rejects(self):
        def failed(source):
            evidence = clean_evidence(source)
            evidence["targets"]["vm"] = {"status": "FAIL", "matched": False, "exit_code": 1, "stdout": "", "stderr": "error"}
            return evidence
        result = validate_deterministic(SOURCE, target_runner=failed)
        self.assertFalse(result["accepted"])
        self.assertIn("TARGET_GATE_FAILED", {item["code"] for item in result["diagnostic"]})

    def test_identical_failures_are_not_differential_pass(self):
        def failed(source):
            evidence = clean_evidence(source)
            for name in REQUIRED_TARGETS:
                evidence["targets"][name] = {"status": "FAIL", "matched": False, "exit_code": 1, "stdout": "", "stderr": "error"}
            evidence["differential_ok"] = True
            return evidence
        result = validate_deterministic(SOURCE, target_runner=failed)
        self.assertFalse(result["accepted"])
        self.assertIn("DIFFERENTIAL_GATE_FAILED", {item["code"] for item in result["diagnostic"]})

    def test_nonzero_exit_is_not_pass(self):
        result = _run_command([sys.executable, "-c", "raise SystemExit(1)"], ROOT / "tests" / "conformance" / FIXTURE["source"])
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["exit_code"], 1)

    def test_all_verified_evidence_gates_can_pass(self):
        result = validate_deterministic(SOURCE, target_runner=clean_evidence)
        self.assertTrue(result["accepted"], result["diagnostic"])

if __name__ == "__main__":
    unittest.main()
