#!/usr/bin/env python3
"""Compare observed reference/native behavior from a fixture matrix."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


FIELDS = ("exit_code", "stdout", "stderr_class", "source_line")


def load_results(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read matrix results at {path}: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("matrix results must be a list")
    return data


def compare(results: list[dict]) -> dict:
    comparisons = []
    mismatches = []
    incomplete = []
    unsupported = []
    for row in results:
        fixture_id = row.get("id", "unknown")
        targets = row.get("targets", {})
        reference = targets.get("reference", {})
        native = targets.get("native", {})
        ref_status, native_status = reference.get("status"), native.get("status")
        if ref_status == "unsupported" or native_status == "unsupported":
            unsupported.append(fixture_id)
            comparisons.append({"id": fixture_id, "status": "unsupported"})
            continue
        if not all(field in reference and field in native for field in FIELDS):
            incomplete.append(fixture_id)
            comparisons.append({"id": fixture_id, "status": "incomplete",
                                "reference_status": ref_status, "native_status": native_status})
            continue
        differences = {
            field: {"reference": reference[field], "native": native[field]}
            for field in FIELDS if reference[field] != native[field]
        }
        status = "fail" if differences else "pass"
        comparison = {"id": fixture_id, "status": status, "differences": differences}
        comparisons.append(comparison)
        if differences:
            mismatches.append(comparison)
    return {
        "schema_version": 1,
        "status": "pass" if not mismatches and not incomplete else "fail",
        "ok": not mismatches and not incomplete,
        "complete": not incomplete,
        "compared": len(comparisons) - len(unsupported) - len(incomplete),
        "mismatch_count": len(mismatches),
        "incomplete_count": len(incomplete),
        "unsupported_count": len(unsupported),
        "regressions": [item["id"] for item in mismatches],
        "incomplete": incomplete,
        "unsupported": unsupported,
        "comparisons": comparisons,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = compare(load_results(args.results))
    except ValueError as exc:
        print(f"DIFFERENTIAL REPORT ERROR: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Differential {report['status'].upper()}: compared={report['compared']}, "
          f"mismatches={report['mismatch_count']}, incomplete={report['incomplete_count']}, "
          f"unsupported={report['unsupported_count']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
