#!/usr/bin/env python3
"""Backward-compatible launcher; canonical implementation lives in tools/datacenter_v6.py."""
from tools.datacenter_v6 import main

if __name__ == "__main__":
    raise SystemExit(main())
