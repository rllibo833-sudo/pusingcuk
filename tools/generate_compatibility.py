#!/usr/bin/env python3
"""Generate or verify fixture counts and conformance snapshots from checked-in data."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "conformance" / "manifest.json"
FIXTURE_START = "<!-- BEGIN GENERATED FIXTURE COUNTS -->"
FIXTURE_END = "<!-- END GENERATED FIXTURE COUNTS -->"
START = "<!-- BEGIN GENERATED CONFORMANCE SUMMARY -->"
END = "<!-- END GENERATED CONFORMANCE SUMMARY -->"
TARGET_ORDER = ("reference", "native", "javascript", "python_transpiler", "html", "vm")
COUNT_KEYS = ("passed", "failed", "timeout", "unsupported", "unavailable")


def render(summary: dict) -> str:
    targets = summary.get("targets")
    if not isinstance(targets, dict):
        raise ValueError("summary must contain a targets object")
    fixture_count = summary.get("fixture_count")
    if not isinstance(fixture_count, int) or isinstance(fixture_count, bool) or fixture_count < 0:
        raise ValueError("summary.fixture_count must be a non-negative integer")
    rows = []
    for name in TARGET_ORDER:
        target = targets.get(name)
        if not isinstance(target, dict):
            raise ValueError(f"summary is missing target {name}")
        values = []
        for key in COUNT_KEYS:
            value = target.get(key, 0)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"summary.targets.{name}.{key} must be a non-negative integer")
            values.append(value)
        if sum(values) != fixture_count:
            raise ValueError(f"summary.targets.{name} counts must add up to fixture_count")
        rows.append("| " + name + " | " + " | ".join(str(value) for value in values) + " |")

    native = targets["native"]
    numerator, denominator = native["passed"], fixture_count
    percent = round(100 * numerator / denominator, 2) if denominator else 0.0

    return "\n".join([
        START,
        "## Measured conformance snapshot",
        "",
        "This table is generated from the supplied machine-readable fixture summary. It is a snapshot, not a live CI result or a claim of complete language compatibility.",
        "",
        "| Target | Passed | Failed | Timeout | Unsupported | Unavailable |",
        "|---|---:|---:|---:|---:|---:|",
        *rows,
        "",
        f"- Fixtures in checked-in baseline summary: **{fixture_count}**",
        f"- Native C Python-free score: **{float(percent):.2f}%** ({numerator}/{denominator}; unsupported fixtures remain in the denominator)",
        END,
    ])


def render_fixture_counts(manifest: dict) -> str:
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("manifest.fixtures must be a non-empty list")
    ids = [item.get("id") for item in fixtures if isinstance(item, dict)]
    if len(ids) != len(fixtures) or any(not isinstance(item, str) or not item for item in ids):
        raise ValueError("every manifest fixture must have a non-empty id")
    if len(set(ids)) != len(ids):
        raise ValueError("manifest fixture IDs must be unique")
    reference_required = sum(1 for item in fixtures if item.get("runtimes", {}).get("reference") == "required")
    native_required = sum(1 for item in fixtures if item.get("runtimes", {}).get("native") == "required")
    native_unsupported = sum(1 for item in fixtures if item.get("runtimes", {}).get("native") == "unsupported")
    return "\n".join([
        FIXTURE_START,
        f"**Active manifest:** **{len(fixtures)} fixtures**; reference required: **{reference_required}**; native C required: **{native_required}**; native C unsupported: **{native_unsupported}**.",
        "These figures are generated directly from `tests/conformance/manifest.json`; CI fails if the checked-in baseline summary disagrees with the manifest count or runtime-status totals.",
        FIXTURE_END,
    ])


def replace_generated_section(document: str, start_marker: str, end_marker: str, generated: str, label: str) -> str:
    if document.count(start_marker) != 1 or document.count(end_marker) != 1:
        raise ValueError(f"{label} must contain each generated marker exactly once")
    before, remainder = document.split(start_marker, 1)
    _, after = remainder.split(end_marker, 1)
    return before.rstrip() + "\n\n" + generated + after


def validate_summary_against_manifest(summary: dict, manifest: dict) -> None:
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or summary.get("fixture_count") != len(fixtures):
        count = len(fixtures) if isinstance(fixtures, list) else "invalid"
        raise ValueError(f"baseline summary fixture_count ({summary.get('fixture_count')!r}) does not match manifest count ({count})")
    targets = summary.get("targets")
    if not isinstance(targets, dict):
        raise ValueError("summary must contain a targets object")
    for target, values in targets.items():
        if not isinstance(values, dict):
            raise ValueError(f"summary.targets.{target} must be an object")
        total = sum(values.get(key, 0) for key in COUNT_KEYS)
        if total != len(fixtures):
            raise ValueError(f"summary.targets.{target} totals {total}, manifest has {len(fixtures)} fixtures")
    native = targets.get("native", {})
    expected_native_unsupported = sum(1 for item in fixtures if item.get("runtimes", {}).get("native") == "unsupported")
    if native.get("unsupported") != expected_native_unsupported:
        raise ValueError(f"baseline native unsupported count ({native.get('unsupported')!r}) does not match manifest ({expected_native_unsupported})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=ROOT / "tests/conformance/baseline_summary.json")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--document", type=Path, default=ROOT / "docs/COMPATIBILITY.md")
    parser.add_argument("--conformance-document", type=Path, default=ROOT / "docs/CONFORMANCE_FIXTURES.md")
    parser.add_argument("--check", action="store_true", help="fail if generated docs are stale or summary mismatches manifest")
    args = parser.parse_args()
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        validate_summary_against_manifest(summary, manifest)
        compatibility = args.document.read_text(encoding="utf-8")
        conformance = args.conformance_document.read_text(encoding="utf-8")
        generated_compatibility = render(summary)
        generated_fixtures = render_fixture_counts(manifest)
        updated_compatibility = replace_generated_section(compatibility, START, END, generated_compatibility, "COMPATIBILITY.md")
        updated_conformance = replace_generated_section(conformance, FIXTURE_START, FIXTURE_END, generated_fixtures, "CONFORMANCE_FIXTURES.md")
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"COMPATIBILITY GENERATOR ERROR: {exc}", file=sys.stderr)
        return 2
    if args.check:
        if updated_compatibility != compatibility:
            print("COMPATIBILITY.md generated section is stale; run tools/generate_compatibility.py", file=sys.stderr)
            return 1
        if updated_conformance != conformance:
            print("CONFORMANCE_FIXTURES.md generated section is stale; run tools/generate_compatibility.py", file=sys.stderr)
            return 1
        print("Generated compatibility and fixture-count sections are current; baseline summary matches manifest.")
        return 0
    try:
        args.document.write_text(updated_compatibility, encoding="utf-8")
        args.conformance_document.write_text(updated_conformance, encoding="utf-8")
    except OSError as exc:
        print(f"COMPATIBILITY GENERATOR ERROR: cannot write generated docs: {exc}", file=sys.stderr)
        return 2
    print("Updated generated compatibility and fixture-count sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
