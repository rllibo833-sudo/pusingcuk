"""Regression guards against the retired autonomous V6 mutation/push loop."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class V6EvolutionSafetyTests(unittest.TestCase):
    def test_legacy_entrypoints_are_review_only(self):
        for name in ("datacenter_v6.py", "V6_CLEAN.py", "fix_parser_all.py"):
            source = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertNotIn("while True", source)
                self.assertNotIn("subprocess", source)
                self.assertNotIn('subprocess.run(["git"', source.lower())
                self.assertNotIn(".write_text(", source)
                self.assertIn("review", source.lower())

    def test_datacenter_is_dry_run(self):
        source = (ROOT / "datacenter_v6.py").read_text(encoding="utf-8")
        self.assertIn("inspect_proposal", source)
        self.assertIn('"DRY-RUN"', source)
        self.assertIn('"git_side_effects"', source)

if __name__ == "__main__":
    unittest.main()
