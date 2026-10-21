#!/usr/bin/env python3
"""Validate target manifests against the single canonical fixture contract.

Target manifests are selectors only: they may list canonical fixture IDs, but
cannot redefine sources, expected outputs, error classes, or source locations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "tests" / "conformance" / "manifest.json"
DEFAULT_TARGETS = ("cpp_manifest.json", "go_manifest.json", "browser_manifest.json")


def validate(canonical_path: Path = CANONICAL, target_paths=None) -> list[str]:
    errors: list[str] = []
    try:
        canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"canonical manifest cannot be read: {exc}"]

    fixtures = canonical.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        return ["canonical manifest must contain a non-empty fixtures array"]

    by_id = {}
    for index, fixture in enumerate(fixtures):
        if not isinstance(fixture, dict) or not isinstance(fixture.get("id"), str):
            errors.append(f"canonical fixture at index {index} has no string id")
            continue
        fixture_id = fixture["id"]
        if fixture_id in by_id:
            errors.append(f"duplicate canonical fixture id: {fixture_id}")
        by_id[fixture_id] = fixture
        source = fixture.get("source")
        if not isinstance(source, str) or not source:
            errors.append(f"{fixture_id}: missing source")
        elif not (canonical_path.parent / source).is_file():
            errors.append(f"{fixture_id}: source file does not exist: {source}")
        expected = fixture.get("expected")
        if not isinstance(expected, dict) or not {"exit_code", "stdout", "stderr_class"} <= expected.keys():
            errors.append(f"{fixture_id}: incomplete canonical expected contract")

    paths = target_paths or [canonical_path.parent / name for name in DEFAULT_TARGETS]
    for path in paths:
        try:
            target = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.name}: cannot be read: {exc}")
            continue
        selected = target.get("fixtures")
        if not isinstance(selected, list):
            errors.append(f"{path.name}: fixtures must be an array of canonical IDs")
            continue
        seen = set()
        for fixture_id in selected:
            if not isinstance(fixture_id, str):
                errors.append(f"{path.name}: target entries must be string fixture IDs")
                continue
            if fixture_id in seen:
                errors.append(f"{path.name}: duplicate fixture ID: {fixture_id}")
            seen.add(fixture_id)
            if fixture_id not in by_id:
                errors.append(f"{path.name}: unknown canonical fixture ID: {fixture_id}")
        forbidden = set(target) - {"schema_version", "description", "fixtures"}
        if forbidden:
            errors.append(
                f"{path.name}: target manifest may only select IDs; unexpected keys: "
                + ", ".join(sorted(forbidden))
            )
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, default=CANONICAL)
    parser.add_argument("targets", nargs="*", type=Path, help="target manifest paths")
    args = parser.parse_args(argv)
    errors = validate(args.canonical, args.targets or None)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print("Target manifests are valid selectors of the canonical fixture contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
