#!/usr/bin/env python3
"""Backward-compatible, review-only DRY-RUN launcher for V6 evolution proposals."""
from tools.datacenter_v6 import inspect_proposal, main

MODE = "DRY-RUN"
GIT_SIDE_EFFECTS = False
SAFETY_CONTRACT = {"git_side_effects": False, "mode": "DRY-RUN", "review_only": True}

# Keep this import visible for legacy safety checks and downstream callers.
__all__ = ["inspect_proposal", "main"]

if __name__ == "__main__":
    raise SystemExit(main())
