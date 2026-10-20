import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class PackagedConformanceManifestTests(unittest.TestCase):
    def test_packaged_manifest_matches_canonical_fixture_manifest(self):
        canonical=json.loads((ROOT/"tests"/"conformance"/"manifest.json").read_text(encoding="utf-8"))
        packaged=json.loads((ROOT/"library"/"conformance_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(packaged,canonical)
        ids=[x["id"] for x in packaged["fixtures"]]
        self.assertEqual(len(ids),len(set(ids))); self.assertGreater(len(ids),0)
if __name__=="__main__": unittest.main()
