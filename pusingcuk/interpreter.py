"""Side-effect-free package entry point for the legacy interpreter API."""
from __future__ import annotations

from interpreter import run as _run


def run(source: str, filename: str = "<input>"):
    """Execute source text through the maintained evaluator contract."""
    return _run(source, filename=filename)


__all__ = ["run"]
