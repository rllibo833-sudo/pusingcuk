#!/usr/bin/env python3
"""Compare observable fixture results across compiler targets without changing backend code."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TARGETS = ("javascript", "python_transpiler", "vm")
CATEGORIES = ("diagnostics_only", "wrong_stdout", "wrong_exit_code", "compile_or_other", "match")


def classify(reference: dict, target: dict) -> str:
    """Return one exclusive difference category relative to the reference runtime."""
    if "exit_code" not in reference or "stdout" not in reference:
        return "compile_or_other"
    if "exit_code" not in target or "stdout" not in target:
        return "compile_or_other"
    if target["stdout"] != reference["stdout"]:
        return "wrong_stdout"
    if target["exit_code"] != reference["exit_code"]:
        return "wrong_exit_code"
    if (
        target.get("stderr_class") != reference.get("stderr_class")
        or target.get("source_line") != reference.get("source_line")
    ):
        return "diagnostics_only"
    return "match"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="per-fixture results.json from ci_fixture_matrix.py")
    parser.add_argument("--output", type=Path, help="write a JSON differential report")
    args = parser.parse_args()
    try:
        rows = json.loads(args.results.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"DIFFERENTIAL RUNNER ERROR: cannot read results: {exc}", file=sys.stderr)
        return 2
    if not isinstance(rows, list):
        print("DIFFERENTIAL RUNNER ERROR: results must be a JSON array", file=sys.stderr)
        return 2

    report = {
        "schema_version": 1,
        "comparison": "actual observable results relative to reference",
        "note": "Diagnostic-only means stdout and exit code match but stderr class or source line differs. Compile failures and missing observations are separate.",
        "targets": {},
    }
    for target_name in TARGETS:
        counts = {category: 0 for category in CATEGORIES}
        cases = []
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("targets"), dict):
                print("DIFFERENTIAL RUNNER ERROR: malformed per-fixture row", file=sys.stderr)
                return 2
            reference = row["targets"].get("reference", {})
            target = row["targets"].get(target_name, {})
            category = classify(reference, target)
            counts[category] += 1
            if category != "match":
                cases.append({
                    "fixture_id": row.get("id"),
                    "category": category,
                    "reference": {
                        key: reference.get(key)
                        for key in ("status", "exit_code", "stdout", "stderr_class", "source_line", "reason")
                        if key in reference
                    },
                    "target": {
                        key: target.get(key)
                        for key in ("status", "exit_code", "stdout", "stderr_class", "source_line", "reason")
                        if key in target
                    },
                })
        report["targets"][target_name] = {"counts": counts, "mismatches": cases}

    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded, encoding="utf-8")
        except OSError as exc:
            print(f"DIFFERENTIAL RUNNER ERROR: cannot write report: {exc}", file=sys.stderr)
            return 2
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
