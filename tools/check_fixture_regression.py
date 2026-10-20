#!/usr/bin/env python3
"""Fail when a conformance target's passed-fixture count falls below the checked-in baseline."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def read_summary(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid summary JSON at {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("targets"), dict):
        raise ValueError(f"{path} must contain a 'targets' object")
    return data


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python tools/check_fixture_regression.py ACTUAL_SUMMARY BASELINE_SUMMARY", file=sys.stderr)
        return 2
    try:
        actual = read_summary(Path(sys.argv[1]))
        baseline = read_summary(Path(sys.argv[2]))
    except ValueError as exc:
        print(f"FIXTURE REGRESSION CHECK ERROR: {exc}", file=sys.stderr)
        return 2

    errors = []
    baseline_count = baseline.get("fixture_count")
    actual_count = actual.get("fixture_count")
    if not isinstance(baseline_count, int) or not isinstance(actual_count, int):
        errors.append("fixture_count must be an integer in both summaries")
    elif actual_count < baseline_count:
        errors.append(f"fixture count decreased {baseline_count} -> {actual_count}; fixtures may have been removed")

    for target, expected in baseline["targets"].items():
        if not isinstance(expected, dict) or not isinstance(expected.get("passed"), int):
            errors.append(f"{target}: baseline passed count is missing or invalid")
            continue
        observed = actual["targets"].get(target)
        if not isinstance(observed, dict) or not isinstance(observed.get("passed"), int):
            errors.append(f"{target}: actual passed count is missing or invalid")
            continue
        before, now = expected["passed"], observed["passed"]
        if now < before:
            errors.append(f"{target}: passed fixtures regressed {before} -> {now} (-{before - now})")
        for metric in ("failed", "timeout", "unavailable"):
            before_bad = expected.get(metric, 0)
            now_bad = observed.get(metric, 0)
            if not isinstance(before_bad, int) or not isinstance(now_bad, int):
                errors.append(f"{target}: {metric} count is missing or invalid")
            elif now_bad > before_bad:
                errors.append(f"{target}: {metric} count increased {before_bad} -> {now_bad} (+{now_bad - before_bad})")
        if now >= before and all(observed.get(metric, 0) <= expected.get(metric, 0) for metric in ("failed", "timeout", "unavailable")):
            print(f"PASS {target}: passed {before} -> {now}; failed {expected.get('failed', 0)} -> {observed.get('failed', 0)}")

    extra_targets = sorted(set(actual["targets"]) - set(baseline["targets"]))
    for target in extra_targets:
        print(f"INFO {target}: no baseline threshold yet; current passed={actual['targets'][target].get('passed')}")

    if errors:
        print("FIXTURE REGRESSION CHECK FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("FIXTURE REGRESSION CHECK PASSED: no target's passed count is below the checked-in baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
