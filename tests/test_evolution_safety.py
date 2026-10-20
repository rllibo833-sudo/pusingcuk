import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools.evolve_daemon import inspect_proposal
from tools.evolve_language import propose

ROOT = Path(__file__).resolve().parents[1]
VOCABULARY = ROOT / "library" / "kosakata.json"


class EvolutionSafetyTests(unittest.TestCase):
    def test_alias_proposal_is_review_only_and_does_not_mutate_vocabulary(self):
        before = hashlib.sha256(VOCABULARY.read_bytes()).hexdigest()
        result = inspect_proposal("hedeh", "proposal_only_alias")
        after = hashlib.sha256(VOCABULARY.read_bytes()).hexdigest()

        self.assertEqual(before, after)
        self.assertEqual(result["status"], "review_required")
        self.assertFalse(result["ok"])
        self.assertEqual(result["proposal"], {
            "canonical": "hedeh",
            "alias": "proposal_only_alias",
        })

    def test_existing_alias_is_rejected_without_mutation(self):
        before = hashlib.sha256(VOCABULARY.read_bytes()).hexdigest()
        result = propose("hedeh", "spill")
        after = hashlib.sha256(VOCABULARY.read_bytes()).hexdigest()

        self.assertEqual(before, after)
        self.assertEqual(result["status"], "rejected")

    def test_daemon_cli_is_finite_and_review_only(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "evolve_daemon.py"),
                "--canonical", "hedeh",
                "--alias", "proposal_only_alias",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "review_required")


if __name__ == "__main__":
    unittest.main()
