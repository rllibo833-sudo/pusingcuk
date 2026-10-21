"""Guard the single-source-of-truth conformance manifest policy."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_target_manifests import validate


class TargetManifestGovernanceTests(unittest.TestCase):
    def test_repository_target_manifests_only_select_canonical_ids(self):
        self.assertEqual(validate(), [])

    def test_rejects_unknown_and_duplicate_fixture_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = root / "manifest.json"
            canonical.write_text(json.dumps({
                "schema_version": 1,
                "fixtures": [{
                    "id": "one.fixture",
                    "source": "one.cuk",
                    "expected": {"exit_code": 0, "stdout": "ok\\n", "stderr_class": None},
                }],
            }), encoding="utf-8")
            (root / "one.cuk").write_text("njir \"ok\"\\n", encoding="utf-8")
            target = root / "target.json"
            target.write_text(json.dumps({
                "schema_version": 1,
                "fixtures": ["one.fixture", "one.fixture", "missing.fixture"],
            }), encoding="utf-8")
            errors = validate(canonical, [target])
            self.assertTrue(any("duplicate fixture ID" in error for error in errors))
            self.assertTrue(any("unknown canonical fixture ID" in error for error in errors))

    def test_rejects_target_specific_expected_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = root / "manifest.json"
            canonical.write_text(json.dumps({
                "schema_version": 1,
                "fixtures": [{
                    "id": "one.fixture",
                    "source": "one.cuk",
                    "expected": {"exit_code": 0, "stdout": "ok\\n", "stderr_class": None},
                }],
            }), encoding="utf-8")
            (root / "one.cuk").write_text("njir \"ok\"\\n", encoding="utf-8")
            target = root / "target.json"
            target.write_text(json.dumps({
                "schema_version": 1,
                "fixtures": ["one.fixture"],
                "expected": {"one.fixture": {"exit_code": 1}},
            }), encoding="utf-8")
            errors = validate(canonical, [target])
            self.assertTrue(any("unexpected keys" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
