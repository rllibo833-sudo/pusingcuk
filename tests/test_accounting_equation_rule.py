"""Regression tests for the registered accounting-equation .cuk rule."""
import unittest

from library.ai_tools import ToolRegistry, _REGISTERED_RULES, _load_rule_source


class AccountingEquationRuleTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry([])

    def test_rule_is_registered_and_hash_pinned(self):
        rule = _REGISTERED_RULES["accounting.equation.v1"]
        import hashlib
        self.assertEqual(hashlib.sha256(_load_rule_source(rule)).hexdigest(), rule["source_sha256"])
        self.assertEqual(rule["capabilities"], ())

    def test_balanced_and_unbalanced_equations(self):
        cases = (
            (1000, 300, 700, "PERSAMAAN_SEIMBANG"),
            (1000, 300, 699, "PERSAMAAN_TIDAK_SEIMBANG"),
            (0, 0, 0, "PERSAMAAN_SEIMBANG"),
            (1000000000000, 250000000000, 750000000000, "PERSAMAAN_SEIMBANG"),
        )
        for aset, liabilitas, ekuitas, expected in cases:
            with self.subTest(aset=aset, liabilitas=liabilitas, ekuitas=ekuitas):
                result = self.registry.execute("accounting_equation_check", {
                    "aset": aset,
                    "liabilitas": liabilitas,
                    "ekuitas": ekuitas,
                })
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["program_id"], "accounting.equation.v1")
                self.assertEqual(result["capabilities"], [])

    def test_invalid_arguments_are_rejected(self):
        cases = (
            {"aset": 1, "liabilitas": 0},
            {"aset": 1, "liabilitas": 0, "ekuitas": 0, "shell": "id"},
            {"aset": True, "liabilitas": 0, "ekuitas": 0},
            {"aset": -1, "liabilitas": 0, "ekuitas": 0},
            {"aset": 1000000000001, "liabilitas": 0, "ekuitas": 0},
        )
        for arguments in cases:
            with self.subTest(arguments=arguments):
                result = self.registry.execute("accounting_equation_check", arguments)
                self.assertFalse(result["ok"])
                self.assertIn(result["error"], {
                    "TOOL_ARGUMENTS_INVALID", "RULE_INPUT_INVALID",
                })


if __name__ == "__main__":
    unittest.main()
