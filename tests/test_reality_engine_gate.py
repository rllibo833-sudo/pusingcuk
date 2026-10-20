"""Fail-closed tests for the Cuk Reality Engine proposal gate."""
import unittest

from tools.reality_engine import validate_deterministic


def clean_evidence(source):
    return {
        "targets": {
            name: {"status": "PASS", "matched": True}
            for name in ("reference", "native", "javascript", "python", "vm")
        },
        "fixture_added": True,
        "fixture_id": "test-regression-1",
        "differential_ok": True,
        "regressions": [],
    }


class RealityEngineGateTests(unittest.TestCase):
    def test_nondeterministic_proposal_is_rejected_before_targets(self):
        called = []
        source = 'jancuk\nhedeh jam()\nselesai jancuk'
        result = validate_deterministic(source, target_runner=lambda text: called.append(text) or clean_evidence(text))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["diagnostic"][0]["code"], "NON_DETERMINISTIC")
        self.assertEqual(called, [])

    def test_fixture_failure_rejects_proposal(self):
        def failed_fixture(source):
            evidence = clean_evidence(source)
            evidence["fixture_added"] = False
            evidence["fixture_id"] = None
            return evidence
        source = 'jancuk\nhedeh "aman"\nselesai jancuk'
        result = validate_deterministic(source, target_runner=failed_fixture)
        self.assertFalse(result["accepted"])
        self.assertIn("FIXTURE_REQUIRED", {item["code"] for item in result["diagnostic"]})

    def test_any_backend_failure_rejects_proposal(self):
        def failed_backend(source):
            evidence = clean_evidence(source)
            evidence["targets"]["vm"] = {"status": "FAIL", "matched": False, "error": "fixture mismatch"}
            return evidence
        source = 'jancuk\nhedeh "aman"\nselesai jancuk'
        result = validate_deterministic(source, target_runner=failed_backend)
        self.assertFalse(result["accepted"])
        self.assertIn("TARGET_GATE_FAILED", {item["code"] for item in result["diagnostic"]})

    def test_acceptance_requires_all_evidence_gates(self):
        source = 'jancuk\nhedeh "aman"\nselesai jancuk'
        result = validate_deterministic(source, target_runner=clean_evidence)
        self.assertTrue(result["accepted"], result["diagnostic"])


if __name__ == "__main__":
    unittest.main()
