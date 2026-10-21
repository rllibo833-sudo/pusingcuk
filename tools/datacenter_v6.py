#!/usr/bin/env python3
"""V6 compatibility entry point: dry-run, review-only language-evolution proposal."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.evolve_daemon import inspect_proposal

ROOT = Path(__file__).resolve().parents[1]
FALLBACK = ("jedor", "gebber", "bacrit", "nyalak", "muncrat", "semprot", "senggol", "berak", "crot", "koar2")


def main(argv=None):
    parser = argparse.ArgumentParser(description="V6 dry-run proposal; no file writes or Git push.")
    parser.add_argument("--canonical", default="hedeh")
    parser.add_argument("--alias")
    args = parser.parse_args(argv)

    if args.alias:
        alias = args.alias
    else:
        try:
            data = json.loads((ROOT / "library" / "kosakata.json").read_text(encoding="utf-8"))
            entries = {
                item.get("word"): set(item.get("aliases", []))
                for item in data.get("keywords", [])
                if isinstance(item, dict)
            }
            used = entries.get(args.canonical, set())
        except (OSError, json.JSONDecodeError) as exc:
            print(json.dumps({"status": "rejected", "reason": str(exc)}))
            return 1
        alias = next((word for word in FALLBACK if word != args.canonical and word not in used), "v6_candidate")

    result = inspect_proposal(args.canonical, alias)
    result.update({"mode": "DRY-RUN", "writes_files": False, "git_side_effects": False})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "review_required" else 1


if __name__ == "__main__":
    raise SystemExit(main())
