import unittest

from compiler.offline_repair import ExactRepairRule, OfflineRepairAdapter


class OfflineRepairAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = OfflineRepairAdapter({
            "replace-output-alias": ExactRepairRule(
                "replace-output-alias", "spill(42)", "tulis(42)"
            )
        })

    def test_applies_exact_registered_rule_without_network(self):
        self.assertEqual(
            self.adapter.propose("replace-output-alias", "spill(42)\n", ""),
            "tulis(42)\n",
        )

    def test_unknown_rule_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unknown offline repair rule"):
            self.adapter.propose("guess", "spill(42)", "")

    def test_missing_match_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "did not match"):
            self.adapter.propose("replace-output-alias", "tulis(42)", "")

    def test_multiple_matches_fail_as_ambiguous(self):
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.adapter.propose(
                "replace-output-alias", "spill(42)\nspill(42)\n", ""
            )

    def test_rule_must_be_valid_and_change_source(self):
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            ExactRepairRule("x", "", "y")
        with self.assertRaisesRegex(ValueError, "must change source"):
            ExactRepairRule("x", "same", "same")

    def test_rule_registry_key_must_match_rule_id(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            OfflineRepairAdapter({
                "wrong-key": ExactRepairRule("actual-id", "a", "b")
            })


if __name__ == "__main__":
    unittest.main()
