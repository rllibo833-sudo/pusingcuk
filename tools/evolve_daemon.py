#!/usr/bin/env python3
"""Safe, opt-in proposal checker for future language-evolution work.

The former daemon edited vocabulary, rewrote app.cuk, committed, and pushed in
an endless loop. That behavior bypassed SPEC.md as the language source of truth
and the Reality Engine acceptance contract. This module intentionally has no
background loop, repository writes, git commands, or network side effects.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCABULARY = ROOT / "library" / "kosakata.json"
SPEC = ROOT / "SPEC.md"


def inspect_proposal(canonical: str, alias: str) -> dict:
    """Return a review-only result; never mutate the repository."""
    try:
        vocabulary = json.loads(VOCABULARY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "status": "rejected", "reason": f"vocabulary unavailable: {exc}"}

    if not alias or not alias.isidentifier():
        return {"ok": False, "status": "rejected", "reason": "alias must be a valid identifier"}
    if not canonical or not canonical.isidentifier():
        return {"ok": False, "status": "rejected", "reason": "canonical keyword must be a valid identifier"}

    existing = {
        item.get("word"): set(item.get("aliases", []))
        for item in vocabulary.get("keywords", [])
        if isinstance(item, dict)
    }
    if canonical not in existing:
        return {"ok": False, "status": "rejected", "reason": "canonical keyword is not in the vocabulary contract"}
    if alias == canonical or alias in existing[canonical]:
        return {"ok": False, "status": "rejected", "reason": "alias already exists or duplicates its canonical keyword"}

    return {
        "ok": False,
        "status": "review_required",
        "reason": "SPEC.md freezes the vocabulary; no alias can be added automatically.",
        "proposal": {"canonical": canonical, "alias": alias},
        "next_step": "Founder review must update SPEC.md, lexer, vocabulary registry, fixtures, and generated docs together.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a language alias proposal without changing files.")
    parser.add_argument("--canonical", required=True, help="existing canonical keyword")
    parser.add_argument("--alias", required=True, help="proposed alias")
    args = parser.parse_args(argv)
    result = inspect_proposal(args.canonical, args.alias)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "review_required" else 1


if __name__ == "__main__":
    raise SystemExit(main())
