import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cuk_ui_runtime", ROOT / "tools" / "cuk_ui_runtime.py")
UI = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = UI
SPEC.loader.exec_module(UI)

class CukUiRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "apps/accounting/cukaccount_frontend.cuk").read_text(encoding="utf-8")
        cls.ui = UI.parse_ui(cls.source)

    def test_primary_navigation_and_screens(self):
        self.assertEqual([x["id"] for x in self.ui["navigation"]], ["home", "transactions", "ledger", "reports", "periods"])
        self.assertEqual({x["id"] for x in self.ui["screens"]}, {"home", "transactions", "ledger", "reports", "periods"})

    def test_journal_amounts_use_integer_fields(self):
        screen = next(s for s in self.ui["screens"] if s["id"] == "transactions")
        fields = {x["id"]: x for x in screen["fields"]}
        self.assertEqual(fields["debit"]["type"], "integer")
        self.assertEqual(fields["credit"]["type"], "integer")
        self.assertIn("required", fields["date"]["rules"])

    def test_html_is_interactive_accessible_and_mobile_responsive(self):
        output = UI.render(self.ui)
        for marker in ('data-route="transactions"', 'data-screen="ledger"', 'aria-label="Navigasi utama"', 'aria-live="polite"', 'theme-toggle', 'data-action="validate"', 'localStorage', '@media(max-width:600px)'):
            self.assertIn(marker, output)

    def test_rejects_invalid_theme_and_navigation(self):
        with self.assertRaises(ValueError): UI.parse_ui(self.source.replace("# @theme system", "# @theme neon"))
        with self.assertRaises(ValueError): UI.parse_ui(self.source.replace("home:Beranda", "missing:Beranda"))

    def test_escapes_labels(self):
        source = self.source.replace("Ringkasan Keuangan", "<script>alert(1)</script>")
        self.assertNotIn("<script>alert(1)</script>", UI.render(UI.parse_ui(source)))
        self.assertIn("&lt;script&gt;", UI.render(UI.parse_ui(source)))

if __name__ == "__main__": unittest.main()
