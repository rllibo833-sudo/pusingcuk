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
README_BADGE_START = "<!-- BEGIN GENERATED PYTHON-FREE SCORE BADGE -->"
README_BADGE_END = "<!-- END GENERATED PYTHON-FREE SCORE BADGE -->"
SCORE_START = "<!-- BEGIN GENERATED PYTHON-FREE SCORE HISTORY -->"
SCORE_END = "<!-- END GENERATED PYTHON-FREE SCORE HISTORY -->"
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


def score_values(summary: dict) -> tuple[int, int, float]:
    fixture_count = summary.get("fixture_count")
    targets = summary.get("targets", {})
    native = targets.get("native", {}) if isinstance(targets, dict) else {}
    numerator = native.get("passed")
    if not isinstance(fixture_count, int) or isinstance(fixture_count, bool) or fixture_count <= 0:
        raise ValueError("summary.fixture_count must be a positive integer for score history")
    if not isinstance(numerator, int) or isinstance(numerator, bool) or not 0 <= numerator <= fixture_count:
        raise ValueError("summary.targets.native.passed must be within the fixture count")
    return numerator, fixture_count, round(100 * numerator / fixture_count, 2)


def render_score_svg(summary: dict) -> str:
    numerator, denominator, percent = score_values(summary)
    label = f"Python-free runtime, native C: {numerator} dari {denominator} fixture"
    left = "Python-free runtime"
    right = f"native C {numerator}/{denominator} fixtures"
    left_width = 120
    right_width = max(116, len(right) * 7 + 16)
    width = left_width + right_width
    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" width="' + str(width) + '" height="20" role="img" aria-label="' + label + '">',
        "  <title>" + label + "</title>",
        '  <linearGradient id="g" x2="0" y2="100%">',
        '    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>',
        '    <stop offset="1" stop-opacity=".1"/>',
        "  </linearGradient>",
        '  <clipPath id="r"><rect width="' + str(width) + '" height="20" rx="3"/></clipPath>',
        '  <g clip-path="url(#r)">',
        '    <rect width="' + str(left_width) + '" height="20" fill="#555"/>',
        '    <rect x="' + str(left_width) + '" width="' + str(right_width) + '" height="20" fill="#287d52"/>',
        '    <rect width="' + str(width) + '" height="20" fill="url(#g)"/>',
        "  </g>",
        '  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">',
        '    <text x="' + str(left_width / 2) + '" y="14">' + left + "</text>",
        '    <text x="' + str(left_width + right_width / 2) + '" y="14">' + right + "</text>",
        "  </g>",
        "</svg>",
        "",
    ])


def validate_score_history(history: dict, summary: dict) -> list[dict]:
    records = history.get("records") if isinstance(history, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("score history must contain at least one record")
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"score history record #{index + 1} must be an object")
        for key in ("date", "commit", "run_url", "numerator", "denominator", "percent"):
            if key not in record:
                raise ValueError(f"score history record #{index + 1} is missing {key}")
        if not isinstance(record["numerator"], int) or isinstance(record["numerator"], bool) or not isinstance(record["denominator"], int) or isinstance(record["denominator"], bool):
            raise ValueError(f"score history record #{index + 1} numerator/denominator must be integers")
        if record["denominator"] <= 0 or not isinstance(record["percent"], (int, float)):
            raise ValueError(f"score history record #{index + 1} has invalid denominator/percent")
        expected = round(100 * record["numerator"] / record["denominator"], 2)
        if round(float(record["percent"]), 2) != expected:
            raise ValueError(f"score history record #{index + 1} percent does not match numerator/denominator")
        if not isinstance(record["commit"], str) or len(record["commit"]) != 40:
            raise ValueError(f"score history record #{index + 1} commit must be a full SHA")
        if not isinstance(record["run_url"], str) or not record["run_url"].startswith("https://github.com/"):
            raise ValueError(f"score history record #{index + 1} run_url must be a GitHub URL")
    numerator, denominator, percent = score_values(summary)
    latest = records[-1]
    if (latest["numerator"], latest["denominator"], round(float(latest["percent"]), 2)) != (numerator, denominator, percent):
        raise ValueError("latest Python-Free Score history record does not match baseline_summary.json; append a new history point before updating the baseline")
    return records


def render_score_history(records: list[dict]) -> str:
    rows = []
    for record in records:
        commit = record["commit"]
        score = f'{float(record["percent"]):.2f}%'
        rows.append(
            f'| {record["date"]} | {score} ({record["numerator"]}/{record["denominator"]}) '
            f'| [`{commit[:7]}`](https://github.com/rllibo833-sudo/pusingcuk/commit/{commit}) '
            f'| [fixture matrix]({record["run_url"]}) |'
        )
    return "\n".join([
        SCORE_START,
        "| Date | Python-Free Score (native C) | Commit | CI evidence |",
        "|---|---:|---|---|",
        *rows,
        SCORE_END,
    ])


def replace_generated_section(document: str, start_marker: str, end_marker: str, generated: str, label: str) -> str:
    if document.count(start_marker) != 1 or document.count(end_marker) != 1:
        raise ValueError(f"{label} must contain each generated marker exactly once")
    before, remainder = document.split(start_marker, 1)
    _, after = remainder.split(end_marker, 1)
    return before.rstrip() + "\n\n" + generated + after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=ROOT / "tests/conformance/baseline_summary.json")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--score-history", type=Path, default=ROOT / "tests/conformance/python_free_score_history.json")
    parser.add_argument("--document", type=Path, default=ROOT / "docs/COMPATIBILITY.md")
    parser.add_argument("--conformance-document", type=Path, default=ROOT / "docs/CONFORMANCE_FIXTURES.md")
    parser.add_argument("--readme", type=Path, default=ROOT / "README.md")
    parser.add_argument("--score-document", type=Path, default=ROOT / "docs/PYTHON_FREE_SCORE.md")
    parser.add_argument("--badge-svg", type=Path, default=ROOT / "docs/assets/python-free-score.svg")
    parser.add_argument("--check", action="store_true", help="fail if generated docs/assets are stale or summary mismatches manifest")
    args = parser.parse_args()
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        history = json.loads(args.score_history.read_text(encoding="utf-8"))
        validate_summary_against_manifest(summary, manifest)
        records = validate_score_history(history, summary)
        compatibility = args.document.read_text(encoding="utf-8")
        conformance = args.conformance_document.read_text(encoding="utf-8")
        readme = args.readme.read_text(encoding="utf-8")
        score_document = args.score_document.read_text(encoding="utf-8")
        old_badge_svg = args.badge_svg.read_text(encoding="utf-8")
        updated_compatibility = replace_generated_section(compatibility, START, END, render(summary), "COMPATIBILITY.md")
        updated_conformance = replace_generated_section(conformance, FIXTURE_START, FIXTURE_END, render_fixture_counts(manifest), "CONFORMANCE_FIXTURES.md")
        badge = f"[![Python-free runtime · native C · {records[-1]['numerator']}/{records[-1]['denominator']} fixtures](docs/assets/python-free-score.svg)](docs/PYTHON_FREE_SCORE.md)"
        score_line = f"Python-free runtime, native C: **{records[-1]['numerator']} dari {records[-1]['denominator']} fixture aktif lulus**. Ini cakupan fixture runtime native C, bukan klaim bahwa seluruh proyek atau proses build bebas Python."
        badge_section = README_BADGE_START + "\n" + badge + "\n" + score_line + "\n" + README_BADGE_END
        updated_readme = replace_generated_section(readme, README_BADGE_START, README_BADGE_END, badge_section, "README.md")
        updated_score_document = replace_generated_section(score_document, SCORE_START, SCORE_END, render_score_history(records), "PYTHON_FREE_SCORE.md")
        updated_badge_svg = render_score_svg(summary)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"COMPATIBILITY GENERATOR ERROR: {exc}", file=sys.stderr)
        return 2
    updates = [
        (args.document, compatibility, updated_compatibility, "COMPATIBILITY.md"),
        (args.conformance_document, conformance, updated_conformance, "CONFORMANCE_FIXTURES.md"),
        (args.readme, readme, updated_readme, "README.md"),
        (args.score_document, score_document, updated_score_document, "PYTHON_FREE_SCORE.md"),
        (args.badge_svg, old_badge_svg, updated_badge_svg, "python-free-score.svg"),
    ]
    if args.check:
        stale = [label for _, original, updated, label in updates if original != updated]
        if stale:
            print("Generated content is stale: " + ", ".join(stale) + "; run tools/generate_compatibility.py", file=sys.stderr)
            return 1
        print("Generated compatibility, fixture counts, score history, README badge and SVG are current; baseline summary matches manifest.")
        return 0
    try:
        for path, _, updated, _ in updates:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(updated, encoding="utf-8")
    except OSError as exc:
        print(f"COMPATIBILITY GENERATOR ERROR: cannot write generated docs/assets: {exc}", file=sys.stderr)
        return 2
    print("Updated generated compatibility, fixture counts, score history, README badge and SVG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
