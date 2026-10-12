#!/usr/bin/env python3
"""CLI terpisah untuk evaluator baru Pusingcuk."""
import argparse
import sys
from pathlib import Path

from evaluator import run
from parser import ParserError


def main():
    parser = argparse.ArgumentParser(
        description="Jalankan program Pusingcuk."
    )
    parser.add_argument("file", help="Berkas sumber Pusingcuk")
    args = parser.parse_args()
    path = Path(args.file)

    if not path.is_file():
        print(f"Kesalahan: berkas tidak ditemukan: {path}", file=sys.stderr)
        return 3

    try:
        source = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Kesalahan: berkas tidak ditemukan: {path}", file=sys.stderr)
        return 3
    except (OSError, UnicodeError) as exc:
        print(f"Kesalahan membaca berkas: {exc}", file=sys.stderr)
        return 1

    try:
        run(source, source_path=path)
    except ParserError as exc:
        print(f"Kesalahan sintaks: {exc}", file=sys.stderr)
        return 2
    except (RuntimeError, ValueError, TypeError, IndexError, OSError) as exc:
        print(f"Kesalahan runtime: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
