"""Prevent documentation version and built-in-count drift."""
import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationContractTests(unittest.TestCase):
    def test_public_docs_match_language_and_package_contract(self):
        package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        contract = json.loads((ROOT / "library/builtin_contract.json").read_text(encoding="utf-8"))
        language = package["tool"]["pusingcuk"]["language-version"]
        package_version = package["project"]["version"]
        total = len(contract["builtins"])
        native = sum(item.get("backends", {}).get("native_c", {}).get("status") == "supported"
                     for item in contract["builtins"])
        self.assertEqual(contract["language_version"], language)
        self.assertEqual(contract["contract_version"], language)
        self.assertEqual((language, package_version, total, native),
                         ("0.5-dev", "0.8.0.dev0", 21, 17))
        expectations = {
            "docs/COMPATIBILITY.md": [f"`{language}`", f"{total} built-in", f"{native} built-in"],
            "docs/VISION.md": [f"`{language}`", f"`{package_version}`"],
            "docs/NATIVE_RUNTIME.md": [f"`{language}`", f"`{package_version}`"],
            "docs/language/BUILTINS.md": [f"`{language}`", f"## {total} Built-in Terkontrak"],
            "docs/PEMULA.md": [f"`{language}`", f"`{package_version}`", f"{total} built-in", f"{native} di antaranya"],
        }
        for relative, phrases in expectations.items():
            content = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, content, f"{relative} missing {phrase!r}")
            self.assertNotIn("0.4-dev", content, f"{relative} has stale language version")
            self.assertNotIn("## 19 Built-in Terkontrak", content)


if __name__ == "__main__":
    unittest.main()
