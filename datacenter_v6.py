#!/usr/bin/env python3
"""Backward-compatible, review-only launcher for the V6 data-center tool."""
from tools.datacenter_v6 import inspect_proposal, main

# Keep this import visible for legacy safety checks and downstream callers.
__all__ = ["inspect_proposal", "main"]

if __name__ == "__main__":
    raise SystemExit(main())
