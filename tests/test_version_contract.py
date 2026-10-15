"""Regression checks for package/runtime/language version metadata coherence."""
import json
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VersionContractTests(unittest.TestCase):
    def test_package_version_matches_all_package_metadata(self):
        package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        lexer = (ROOT / "lexer.py").read_text(encoding="utf-8")
        native = (ROOT / "native" / "pusingcuk.c").read_text(encoding="utf-8")
        android = (ROOT / "scripts" / "build-android.sh").read_text(encoding="utf-8")
        vocabulary = json.loads((ROOT / "library" / "kosakata.json").read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        expected = package["project"]["version"]
        make_match = re.search(r"^VERSION\s*\?=\s*(\S+)\s*$", makefile, re.MULTILINE)
        native_match = re.search(r'^#define\s+PUSINGCUK_VERSION\s+"([^"]+)"\s*$', native, re.MULTILINE)
        android_match = re.search(r"SOURCE_VERSION:-([0-9]+\.[0-9]+\.[0-9]+(?:\.dev[0-9]+)?)\}-android", android)

        self.assertIsNotNone(make_match, "Makefile must declare VERSION")
        self.assertIsNotNone(native_match, "native C must have a package-version fallback")
        self.assertIsNotNone(android_match, "Android build script must have a package-version fallback")
        self.assertEqual(make_match.group(1), expected)
        self.assertEqual(native_match.group(1), expected)
        self.assertEqual(vocabulary["package_version"], expected)
        self.assertEqual(android_match.group(1), expected)
        self.assertIn(f"metadata paket main: {expected}", lexer)
        self.assertIn(f"Metadata paket pada `main` adalah `{expected}`", readme)
        self.assertIn(f"target paket {expected}", changelog)
        self.assertIn("Unreleased", changelog)

    def test_language_contract_version_matches_metadata(self):
        package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        lexer = (ROOT / "lexer.py").read_text(encoding="utf-8")
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        contract = json.loads((ROOT / "library" / "builtin_contract.json").read_text(encoding="utf-8"))
        vocabulary = json.loads((ROOT / "library" / "kosakata.json").read_text(encoding="utf-8"))

        expected = package["tool"]["pusingcuk"]["language-version"]
        self.assertEqual(expected, "0.5-dev")
        self.assertEqual(contract["contract_version"], expected)
        self.assertEqual(contract["language_version"], expected)
        self.assertEqual(vocabulary["language_version"], expected)
        self.assertIn(f"Pusingcuk {expected}", lexer)
        self.assertIn(f"Pusingcuk {expected}", spec)


    def test_python_native_and_vocabulary_aliases_match_spec(self):
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        lexer_source = (ROOT / "lexer.py").read_text(encoding="utf-8")
        native_source = (ROOT / "native" / "pusingcuk.c").read_text(encoding="utf-8")
        vocabulary = json.loads((ROOT / "library" / "kosakata.json").read_text(encoding="utf-8"))

        section = spec[spec.index("## 16. Alias kosakata"):spec.index("## 17.")]
        core_section, api_section = section.split("### Alias API tambahan", 1)

        def parse_spec_aliases(text):
            aliases = {}
            for line in text.splitlines():
                if line.startswith("- `") and "` → `" in line:
                    alias = line.split("`", 2)[1]
                    canonical = line.split("` → `", 1)[1].split("`", 1)[0]
                    aliases[alias] = canonical
            return aliases

        core_aliases = parse_spec_aliases(core_section)
        all_aliases = {**core_aliases, **parse_spec_aliases(api_section)}

        lexer_start = lexer_source.index("KEYWORD_ALIASES = {")
        lexer_body = lexer_source[lexer_start:].split("\n}", 1)[0].split("{", 1)[1]
        python_aliases = {}
        for line in lexer_body.splitlines():
            line = line.strip().rstrip(",")
            if not line:
                continue
            alias, canonical = line.split(":", 1)
            python_aliases[alias.strip().strip('"')] = canonical.strip().strip('"')
        self.assertEqual(python_aliases, all_aliases)

        native_start = native_source.index("static const struct { const char *alias, *canonical; } aliases[] = {")
        native_body = native_source[native_start:].split("\n    };", 1)[0].split("{", 1)[2]
        native_aliases = {}
        for line in native_body.splitlines():
            line = line.strip().rstrip(",")
            if line.startswith('{"') and line.endswith("}"):
                alias, canonical = line[1:-1].split(",", 1)
                native_aliases[alias.strip().strip('"')] = canonical.strip().strip('"')
        self.assertEqual(native_aliases, core_aliases)

        metadata_aliases = {
            alias: item["word"]
            for item in vocabulary["keywords"]
            for alias in item.get("aliases", [])
        }
        self.assertEqual(metadata_aliases, all_aliases)
        self.assertEqual((len(all_aliases), len(core_aliases)), (23, 12))

if __name__ == "__main__":
    unittest.main()
