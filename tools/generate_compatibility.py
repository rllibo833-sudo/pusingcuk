#!/usr/bin/env python3
"""Generate or verify the measured conformance section in docs/COMPATIBILITY.md."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=ROOT / "tests/conformance/baseline_summary.json")
    parser.add_argument("--document", type=Path, default=ROOT / "docs/COMPATIBILITY.md")
    parser.add_argument("--check", action="store_true", help="fail if the generated section is stale")
    args = parser.parse_args()
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
        document = args.document.read_text(encoding="utf-8")
        generated = render(summary)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"COMPATIBILITY GENERATOR ERROR: {exc}", file=sys.stderr)
        return 2
    if document.count(START) != 1 or document.count(END) != 1:
        print("COMPATIBILITY GENERATOR ERROR: document must contain each generated marker exactly once", file=sys.stderr)
        return 2
    before, remainder = document.split(START, 1)
    _, after = remainder.split(END, 1)
    updated = before.rstrip() + "\n\n" + generated + after
    if args.check:
        if updated != document:
            print("COMPATIBILITY.md generated section is stale; run tools/generate_compatibility.py", file=sys.stderr)
            return 1
        print("COMPATIBILITY.md generated section is current.")
        return 0
    try:
        args.document.write_text(updated, encoding="utf-8")
    except OSError as exc:
        print(f"COMPATIBILITY GENERATOR ERROR: cannot write document: {exc}", file=sys.stderr)
        return 2
    print(f"Updated {args.document.relative_to(ROOT) if args.document.is_relative_to(ROOT) else args.document}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
