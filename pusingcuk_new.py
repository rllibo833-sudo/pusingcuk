#!/usr/bin/env python3
"""CLI terpisah untuk evaluator baru Pusingcuk."""
import argparse
import sys
from pathlib import Path

from evaluator import run


def main():
    parser = argparse.ArgumentParser(
        description="Jalankan program Pusingcuk."
    )
    parser.add_argument("file", help="Berkas sumber Pusingcuk")
    args = parser.parse_args()
    path = Path(args.file)

    if not path.is_file():
        print(f"Kesalahan: berkas tidak ditemukan: {path}", file=sys.stderr)
        return 2

    try:
        run(path.read_text(encoding="utf-8"))
    except (SyntaxError, RuntimeError, ValueError, TypeError, IndexError) as exc:
        print(f"Kesalahan: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
