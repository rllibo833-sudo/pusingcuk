"""Compatibility entry point for the manifest-driven conformance runner."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.conformance import main


if __name__ == "__main__":
    raise SystemExit(main())
