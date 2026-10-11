"""Unit tests for the conformance manifest validator."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.conformance import ManifestError, load_manifest


class ConformanceManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "valid.pusingcuk").write_text(
            "jancuk\nhedeh 1\nselesai jancuk\n", encoding="utf-8"
        )
        self.manifest_path = self.root / "manifest.json"

    def fixture(self, **overrides):
        item = {
            "id": "test.valid",
            "source": "valid.pusingcuk",
            "profile": "core",
            "requires": ["output"],
            "expected": {"exit_code": 0, "stdout": "1\n", "stderr_class": None},
            "runtimes": {"reference": "required"},
        }
        item.update(overrides)
        return item

    def write_manifest(self, fixtures, schema_version=1):
        self.manifest_path.write_text(
            json.dumps({"schema_version": schema_version, "fixtures": fixtures}),
            encoding="utf-8",
        )
        return self.manifest_path

    def test_accepts_valid_manifest(self):
        validated = load_manifest(self.write_manifest([self.fixture()]))
        self.assertEqual(len(validated), 1)
        self.assertEqual(validated[0][0]["id"], "test.valid")

    def test_rejects_path_traversal(self):
        outside = self.root.parent / "outside.pusingcuk"
        outside.write_text("jancuk\nselesai jancuk\n", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        with self.assertRaisesRegex(ManifestError, "keluar dari direktori"):
            load_manifest(self.write_manifest([self.fixture(source="../outside.pusingcuk")]))

    def test_rejects_duplicate_ids(self):
        first = self.fixture()
        second = self.fixture(source="valid.pusingcuk")
        with self.assertRaisesRegex(ManifestError, "duplikat"):
            load_manifest(self.write_manifest([first, second]))

    def test_rejects_unknown_runtime(self):
        with self.assertRaisesRegex(ManifestError, "runtime tidak dikenal"):
            load_manifest(self.write_manifest([
                self.fixture(runtimes={"arbitrary-shell": "required"})
            ]))

    def test_rejects_invalid_runtime_state(self):
        with self.assertRaisesRegex(ManifestError, "status runtime tidak valid"):
            load_manifest(self.write_manifest([
                self.fixture(runtimes={"reference": ["required"]})
            ]))

    def test_rejects_unknown_manifest_schema(self):
        with self.assertRaisesRegex(ManifestError, "schema_version"):
            load_manifest(self.write_manifest([self.fixture()], schema_version=99))

    def test_rejects_missing_fixture_file(self):
        with self.assertRaisesRegex(ManifestError, "file .pusingcuk yang ada"):
            load_manifest(self.write_manifest([self.fixture(source="missing.pusingcuk")]))

    def test_rejects_unknown_fields(self):
        with self.assertRaisesRegex(ManifestError, "field tidak dikenal"):
            load_manifest(self.write_manifest([self.fixture(unreviewed_option=True)]))


if __name__ == "__main__":
    unittest.main()
