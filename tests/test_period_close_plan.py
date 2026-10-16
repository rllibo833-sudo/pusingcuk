"""Regression coverage for the registered CukAccount period-close rule."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "library" / "period_close_plan.cuk"


def run_rule(income: str, expense: str) -> list[str]:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "pusingcuk_new.py"), str(RULE)],
        input=f"{income}\n{expense}\n",
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=10,
        check=True,
    )
    return completed.stdout.splitlines()


class PeriodClosePlanTests(unittest.TestCase):
    def test_profit_posts_balanced_closing_plan(self):
        self.assertEqual(
            run_rule("250000", "100000"),
            ["PENUTUPAN_LABA", "150000", "250000", "0", "0", "100000", "0", "150000"],
        )

    def test_loss_posts_balanced_closing_plan(self):
        self.assertEqual(
            run_rule("100000", "250000"),
            ["PENUTUPAN_RUGI", "-150000", "100000", "0", "0", "250000", "150000", "0"],
        )

    def test_zero_result_does_not_create_retained_earnings_line(self):
        self.assertEqual(
            run_rule("100000", "100000"),
            ["PENUTUPAN_NOL", "0", "100000", "0", "0", "100000", "0", "0"],
        )

    def test_rejects_negative_and_over_limit_totals(self):
        self.assertEqual(run_rule("-1", "0"), ["INPUT_TIDAK_VALID"])
        self.assertEqual(run_rule("0", "1000000000001"), ["INPUT_TIDAK_VALID"])
        self.assertEqual(run_rule("1000000000001", "0"), ["INPUT_TIDAK_VALID"])

    def test_rejects_non_numeric_income_or_expense_without_partial_plan(self):
        self.assertEqual(run_rule("abc", "100"), ["INPUT_TIDAK_VALID"])
        self.assertEqual(run_rule("100", "abc"), ["INPUT_TIDAK_VALID"])
        self.assertEqual(run_rule("", "100"), ["INPUT_TIDAK_VALID"])


if __name__ == "__main__":
    unittest.main()
