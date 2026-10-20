#!/usr/bin/env python3
"""Check that language alias tables match the frozen contract in SPEC.md."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "SPEC.md"
ROOT_LEXER = ROOT / "lexer.py"
PACKAGE_LEXER = ROOT / "pusingcuk" / "lexer.py"
NATIVE = ROOT / "native" / "pusingcuk.c"
VOCABULARY = ROOT / "library" / "kosakata.json"


def parse_spec_aliases(text: str) -> tuple[dict[str, str], dict[str, str]]:
    start = text.find("## 16. Alias kosakata")
    end = text.find("## 17.", start)
    if start < 0 or end < 0:
        raise ValueError("SPEC.md tidak memiliki bagian alias 16/17")
    section = text[start:end]
    marker = "### Alias API tambahan"
    if marker not in section:
        raise ValueError("SPEC.md tidak memiliki subbagian Alias API tambahan")
    core_text, api_text = section.split(marker, 1)

    def parse(block: str) -> dict[str, str]:
        aliases: dict[str, str] = {}
        for line in block.splitlines():
            match = re.match(r"^- `([^`]+)` → `([^`]+)`", line)
            if not match:
                continue
            alias, canonical = match.groups()
            if alias in aliases:
                raise ValueError(f"alias duplikat di SPEC.md: {alias}")
            aliases[alias] = canonical
        return aliases

    core = parse(core_text)
    api = parse(api_text)
    overlap = set(core) & set(api)
    if overlap:
        raise ValueError("alias muncul di dua kelompok SPEC.md: " + ", ".join(sorted(overlap)))
    return core, {**core, **api}


def parse_python_aliases(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    start = text.find("KEYWORD_ALIASES = {")
    end = text.find("\n}", start)
    if start < 0 or end < 0:
        raise ValueError(f"KEYWORD_ALIASES tidak ditemukan: {path.relative_to(ROOT)}")
    body = text[start:end]
    return dict(re.findall(r'^\s*"([^"]+)"\s*:\s*"([^"]+)"\s*,?\s*$', body, re.MULTILINE))


def parse_native_aliases(text: str) -> dict[str, str]:
    marker = 'static const struct { const char *alias, *canonical; } aliases[] = {'
    start = text.find(marker)
    end = text.find("\n    };", start)
    if start < 0 or end < 0:
        raise ValueError("tabel alias native C tidak ditemukan")
    body = text[start:end]
    return dict(re.findall(r'\{"([^"]+)",\s*"([^"]+)"\}', body))


def parse_vocabulary(path: Path) -> tuple[dict[str, str], dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("keywords"), list):
        raise ValueError("kosakata.json harus memakai keywords sebagai list")
    aliases: dict[str, str] = {}
    for item in data["keywords"]:
        if not isinstance(item, dict) or not isinstance(item.get("word"), str):
            raise ValueError("entry keywords tidak valid")
        for alias in item.get("aliases", []):
            if alias in aliases:
                raise ValueError(f"alias duplikat di kosakata.json: {alias}")
            aliases[alias] = item["word"]
        if item.get("alias_of"):
            aliases[item["word"]] = item["alias_of"]
    return aliases, data


def difference(actual: dict[str, str], expected: dict[str, str]) -> list[str]:
    issues = []
    for alias in sorted(set(actual) | set(expected)):
        got, want = actual.get(alias), expected.get(alias)
        if got != want:
            issues.append(f"{alias}: actual={got or '—'}; expected={want or '—'}")
    return issues


def main() -> int:
    core, all_aliases = parse_spec_aliases(SPEC_PATH.read_text(encoding="utf-8"))
    root_aliases = parse_python_aliases(ROOT_LEXER)
    package_aliases = parse_python_aliases(PACKAGE_LEXER)
    native_aliases = parse_native_aliases(NATIVE.read_text(encoding="utf-8"))
    vocabulary_aliases, vocabulary = parse_vocabulary(VOCABULARY)

    tables = [
        ("lexer.py", root_aliases, all_aliases),
        ("pusingcuk/lexer.py", package_aliases, all_aliases),
        ("native/pusingcuk.c (alias inti)", native_aliases, core),
        ("library/kosakata.json keywords", vocabulary_aliases, all_aliases),
    ]
    failures = []
    print(f"SPEC.md: {len(core)} alias inti, {len(all_aliases)} alias total")
    print("Alias | SPEC | root lexer | package lexer | native C | kosakata")
    for alias in sorted(all_aliases):
        native_value = native_aliases.get(alias, "— (API tambahan)")
        print(
            f"{alias} | {all_aliases[alias]} | {root_aliases.get(alias, '—')} | "
            f"{package_aliases.get(alias, '—')} | {native_value} | {vocabulary_aliases.get(alias, '—')}"
        )
    for name, actual, expected in tables:
        issues = difference(actual, expected)
        if issues:
            failures.append((name, issues))
    legacy_keys = [key for key in ("Pusingcuk", "0.6-dev", "hedeh_legacy") if key in vocabulary]
    if legacy_keys:
        failures.append(("library/kosakata.json legacy keys", legacy_keys))
    if vocabulary.get("source_of_truth") != "SPEC.md":
        failures.append(("library/kosakata.json source_of_truth", [repr(vocabulary.get("source_of_truth"))]))
    if failures:
        print("\nFAIL: alias contract tidak sinkron", file=sys.stderr)
        for name, issues in failures:
            print(f"- {name}", file=sys.stderr)
            for issue in issues:
                print(f"  {issue}", file=sys.stderr)
        return 1
    print("PASS: seluruh alias sesuai SPEC.md; native C sesuai alias inti.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
