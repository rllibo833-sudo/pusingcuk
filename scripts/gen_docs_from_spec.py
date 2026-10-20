#!/usr/bin/env python3
"""Generate contract tables in README and AI readiness docs from SPEC.md."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START_SPEC = "## 16. Alias kosakata"
END_SPEC = "## 17."
README_START = "<!-- BEGIN GENERATED SPEC ALIASES -->"
README_END = "<!-- END GENERATED SPEC ALIASES -->"
READY_START = "<!-- BEGIN GENERATED LANGUAGE CONTRACT -->"
READY_END = "<!-- END GENERATED LANGUAGE CONTRACT -->"
COMPAT_START = "<!-- BEGIN GENERATED CONFORMANCE SUMMARY -->"
COMPAT_END = "<!-- END GENERATED CONFORMANCE SUMMARY -->"
FIXTURE_START = "<!-- BEGIN GENERATED FIXTURE COUNTS -->"
FIXTURE_END = "<!-- END GENERATED FIXTURE COUNTS -->"
TICK = chr(96)


def parse_aliases(block: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in block.splitlines():
        if not line.startswith("- ") or "→" not in line:
            continue
        parts = line.split(TICK)
        if len(parts) < 5:
            continue
        alias, canonical = parts[1], parts[3]
        if alias in result:
            raise ValueError("alias duplikat dalam SPEC.md: " + alias)
        result[alias] = canonical
    return result


def read_spec() -> tuple[dict[str, str], dict[str, str]]:
    text = (ROOT / "SPEC.md").read_text(encoding="utf-8")
    start = text.find(START_SPEC)
    end = text.find(END_SPEC, start)
    if start < 0 or end < 0:
        raise ValueError("bagian alias SPEC.md tidak ditemukan")
    section = text[start:end]
    marker = "### Alias API tambahan"
    if marker not in section:
        raise ValueError("subbagian Alias API tambahan tidak ditemukan")
    core_text, api_text = section.split(marker, 1)
    core, api = parse_aliases(core_text), parse_aliases(api_text)
    if set(core) & set(api):
        raise ValueError("alias inti dan API tumpang tindih")
    return core, {**core, **api}


def read_lexer_aliases() -> dict[str, str]:
    text = (ROOT / "lexer.py").read_text(encoding="utf-8")
    start = text.find("KEYWORD_ALIASES = {")
    end = text.find("\n}", start)
    if start < 0 or end < 0:
        raise ValueError("KEYWORD_ALIASES tidak ditemukan di lexer.py")
    return dict(re.findall(r'^\s*"([^"]+)"\s*:\s*"([^"]+)"\s*,?\s*$', text[start:end], re.MULTILINE))


def read_vocabulary_aliases() -> dict[str, str]:
    data = json.loads((ROOT / "library" / "kosakata.json").read_text(encoding="utf-8"))
    if data.get("source_of_truth") != ["../SPEC.md"] or not isinstance(data.get("keywords"), list):
        raise ValueError("kosakata.json harus merujuk ke ../SPEC.md dan memakai keywords[]")
    result = {}
    for item in data["keywords"]:
        for alias in item.get("aliases", []):
            if alias in result:
                raise ValueError("alias duplikat di kosakata.json: " + alias)
            result[alias] = item["word"]
    return result


def alias_table(aliases: dict[str, str]) -> str:
    rows = "\n".join("| " + alias + " | " + canonical + " |" for alias, canonical in sorted(aliases.items()))
    return (
        "## Keyword alias reference\n\n"
        "This table is generated from SPEC.md. It documents accepted spellings; it does not add reserved words.\n\n"
        "| Alias | Canonical keyword |\n|---|---|\n" + rows
    )


def replace_block(text: str, start_marker: str, end_marker: str, body: str, anchor: str) -> str:
    replacement = start_marker + "\n" + body + "\n" + end_marker
    if start_marker in text and end_marker in text:
        pattern = re.compile(re.escape(start_marker) + r"[\s\S]*?" + re.escape(end_marker))
        return pattern.sub(lambda _match: replacement, text, count=1)
    if start_marker in text or end_marker in text:
        raise ValueError("marker dokumen tidak berpasangan: " + start_marker)
    if anchor not in text:
        raise ValueError("anchor dokumen tidak ditemukan: " + anchor)
    return text.replace(anchor, replacement + "\n\n" + anchor, 1)


def readiness_table(aliases: dict[str, str]) -> str:
    baseline = json.loads((ROOT / "tests" / "conformance" / "baseline_summary.json").read_text(encoding="utf-8"))
    rows = []
    for target, result in baseline["targets"].items():
        rows.append("| " + target + " | " + str(result["passed"]) + "/" + str(baseline["fixture_count"]) +
                    " | " + str(result.get("failed", 0)) + " | " + str(result.get("unsupported", 0)) + " |")
    alias_rows = "\n".join("| " + alias + " | " + canonical + " |" for alias, canonical in sorted(aliases.items()))
    return (
        "## Generated language-contract and conformance snapshot\n\n"
        "The alias table below is generated from SPEC.md after checking the root lexer and library/kosakata.json. It describes accepted spellings, not new language keywords.\n\n"
        "| Alias | Canonical keyword |\n|---|---|\n" + alias_rows +
        "\n\n### Latest checked-in conformance baseline\n\n"
        "| Target | Passed | Failed | Unsupported |\n|---|---:|---:|---:|\n" + "\n".join(rows) +
        "\n\nThe reference runtime passed " + str(baseline["targets"].get("reference", {}).get("passed", 0)) + "/" + str(baseline["fixture_count"]) + " fixtures in the verified matrix; native C passed " + str(baseline["targets"].get("native", {}).get("passed", 0)) + "/" + str(baseline["fixture_count"]) + " with " + str(baseline["targets"].get("native", {}).get("unsupported", 0)) + " explicitly unsupported fixtures. JavaScript, Python transpiler, and VM remain experimental with substantial parity gaps. HTML has no executable backend in this repository. These counts are fixture evidence, not a general compatibility or production-readiness claim.\n\n"
        "**AI status:** PusingCuk AI remains local/experimental. CI provider-contract tests use mocked providers; CI does not prove live Ollama inference, hosted availability, or production safety. The runtime is not an OS sandbox."
    )


def read_verified_baseline() -> tuple[dict, dict]:
    baseline_path = ROOT / "tests" / "conformance" / "baseline_summary.json"
    manifest_path = ROOT / "tests" / "conformance" / "manifest.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("manifest.json harus memiliki fixtures[] non-kosong")
    if baseline.get("fixture_count") != len(fixtures):
        raise ValueError("baseline_summary.json fixture_count tidak cocok dengan manifest.json")
    targets = baseline.get("targets")
    if not isinstance(targets, dict):
        raise ValueError("baseline_summary.json harus memiliki targets{}")
    for target, counts in targets.items():
        total = sum(int(counts.get(state, 0)) for state in ("passed", "failed", "timeout", "unsupported", "unavailable"))
        if total != len(fixtures):
            raise ValueError(f"baseline target {target} berjumlah {total}, bukan {len(fixtures)} fixture")
    for runtime in ("reference", "native"):
        if runtime not in targets:
            raise ValueError("baseline wajib memiliki target " + runtime)
    return baseline, manifest


def compatibility_snapshot() -> str:
    baseline, _manifest = read_verified_baseline()
    rows = []
    for target, result in baseline["targets"].items():
        rows.append("| " + target + " | " + str(result.get("passed", 0)) + " | " +
                    str(result.get("failed", 0)) + " | " + str(result.get("timeout", 0)) + " | " +
                    str(result.get("unsupported", 0)) + " | " + str(result.get("unavailable", 0)) + " |")
    score = baseline.get("python_free_score", {})
    return (
        "## Measured conformance snapshot\n\n"
        "Generated from the checked-in fixture baseline and validated against the active manifest. This is a snapshot, not a live CI result or a claim of complete language compatibility.\n\n"
        "| Target | Passed | Failed | Timeout | Unsupported | Unavailable |\n"
        "|---|---:|---:|---:|---:|---:|\n" + "\n".join(rows) + "\n\n"
        "- Fixtures in checked-in baseline summary: **" + str(baseline["fixture_count"]) + "**\n"
        "- Native C Python-free score: **" + str(score.get("percent", "unknown")) + "%** (" +
        str(score.get("numerator", "unknown")) + "/" + str(score.get("denominator", "unknown")) +
        "; unsupported fixtures remain in the denominator)"
    )


def fixture_count_snapshot() -> str:
    baseline, manifest = read_verified_baseline()
    fixtures = manifest["fixtures"]
    reference_required = sum(item.get("runtimes", {}).get("reference") == "required" for item in fixtures)
    native_required = sum(item.get("runtimes", {}).get("native") == "required" for item in fixtures)
    native_unsupported = sum(item.get("runtimes", {}).get("native") == "unsupported" for item in fixtures)
    return (
        "**Active manifest:** **" + str(len(fixtures)) + " fixtures**; reference required: **" +
        str(reference_required) + "**; native C required: **" + str(native_required) +
        "**; native C unsupported: **" + str(native_unsupported) + "**.\n"
        "These figures are generated directly from `tests/conformance/manifest.json`; the checked-in baseline summary is validated against the same fixture count and each target's status totals."
    )


def render() -> dict[Path, str]:
    _core, aliases = read_spec()
    if read_lexer_aliases() != aliases:
        raise ValueError("lexer.py tidak sinkron dengan SPEC.md")
    if read_vocabulary_aliases() != aliases:
        raise ValueError("kosakata.json tidak sinkron dengan SPEC.md")
    readme_path = ROOT / "README.md"
    readiness_path = ROOT / "docs" / "AI_ENGINE_READINESS.md"
    readme = replace_block(readme_path.read_text(encoding="utf-8"), README_START, README_END,
                           alias_table(aliases), "## The three parts of the ecosystem")
    readiness = replace_block(readiness_path.read_text(encoding="utf-8"), READY_START, READY_END,
                              readiness_table(aliases), "## Existing project structure to extend, not duplicate")
    compatibility_path = ROOT / "docs" / "COMPATIBILITY.md"
    compatibility = replace_block(compatibility_path.read_text(encoding="utf-8"), COMPAT_START, COMPAT_END,
                                  compatibility_snapshot(), "## Sasaran matriks platform")
    fixtures_path = ROOT / "docs" / "CONFORMANCE_FIXTURES.md"
    fixtures_doc = replace_block(fixtures_path.read_text(encoding="utf-8"), FIXTURE_START, FIXTURE_END,
                                 fixture_count_snapshot(), "Manifest saat ini belum memuat fixture khusus Reality Engine")
    return {
        readme_path: readme,
        readiness_path: readiness,
        compatibility_path: compatibility,
        fixtures_path: fixtures_doc,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail instead of writing if generated docs are stale")
    args = parser.parse_args(argv)
    try:
        rendered = render()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("DOCUMENT GENERATION ERROR: " + str(exc), file=sys.stderr)
        return 2
    stale = []
    for path, expected in rendered.items():
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            if args.check:
                stale.append(path.relative_to(ROOT).as_posix())
            else:
                path.write_text(expected, encoding="utf-8")
                print("Updated " + path.relative_to(ROOT).as_posix())
    if stale:
        print("Generated docs are stale: " + ", ".join(stale), file=sys.stderr)
        return 1
    if args.check:
        print("Generated docs match SPEC.md, lexer.py, kosakata.json, and the checked-in conformance baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
