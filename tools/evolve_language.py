#!/usr/bin/env python3
"""Review-only language evolution helper.

SPEC.md is the canonical vocabulary contract. This helper must never mutate
library/kosakata.json, commit, or push an alias by itself. An approved change
must update the specification, implementation, conformance fixtures, and
generated documentation as one reviewed change.
"""
from __future__ import annotations

import argparse
import json
import sys

from tools.evolve_daemon import inspect_proposal


def propose(canonical: str, new_alias: str) -> dict:
    """Compatibility wrapper returning a review-only proposal result."""
    return inspect_proposal(canonical, new_alias)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Create a review-only alias proposal; no repository files are changed.")
    parser.add_argument("canonical", help="existing canonical keyword")
    parser.add_argument("alias", help="proposed alias")
    args = parser.parse_args(argv)
    result = propose(args.canonical, args.alias)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "review_required" else 1


if __name__ == "__main__":
    raise SystemExit(main())
