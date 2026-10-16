"""Regression tests for the registered accounting-equation .cuk rule."""
import json
import unittest
from pathlib import Path

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

    def test_non_integer_values_are_rejected_without_coercion(self):
        invalid_values = (1.0, "1", None, [], {}, float("nan"), float("inf"))
        for value in invalid_values:
            with self.subTest(value=repr(value)):
                result = self.registry.execute("accounting_equation_check", {
                    "aset": value,
                    "liabilitas": 0,
                    "ekuitas": 0,
                })
                self.assertFalse(result["ok"])
                self.assertEqual(result["error"], "RULE_INPUT_INVALID")

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


    def test_cuk_report_classification_rule_uses_shared_cukaccount_fixture(self):
        import hashlib
        rule = _REGISTERED_RULES["report.classification.v1"]
        source = _load_rule_source(rule)
        self.assertEqual(hashlib.sha256(source).hexdigest(), rule["source_sha256"])
        compiled = self.registry.execute("cuk_compile_check", {"source": source.decode("utf-8")})
        self.assertTrue(compiled["ok"], compiled)
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "cukaccount_financial_acceptance.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        cases = fixture["expected"]["report_classification"]
        self.assertEqual(set(cases), {"complete", "missing_cash_category", "missing_equity_category"})
        for case_id, case in cases.items():
            with self.subTest(case=case_id):
                result = self.registry.execute("report_classification_check", case["input"])
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["result"], case["result"])
        invalid = self.registry.execute("report_classification_check", {
            "jumlah_kas": 1, "kas_tanpa_kategori": 2,
            "jumlah_ekuitas": 0, "ekuitas_tanpa_kategori": 0,
        })
        self.assertTrue(invalid["ok"], invalid)
        self.assertEqual(invalid["result"], "INPUT_TIDAK_VALID")
        invalid_type = self.registry.execute("report_classification_check", {
            "jumlah_kas": True, "kas_tanpa_kategori": 0,
            "jumlah_ekuitas": 0, "ekuitas_tanpa_kategori": 0,
        })
        self.assertFalse(invalid_type["ok"])
        self.assertEqual(invalid_type["error"], "RULE_INPUT_INVALID")


if __name__ == "__main__":
    unittest.main()
