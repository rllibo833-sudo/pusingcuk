#!/usr/bin/env python3
"""CLI terpisah untuk evaluator baru Pusingcuk."""
import argparse
import sys
from pathlib import Path

from evaluator import run
from parser import ParserError, parse as parse_source


def main():
    parser = argparse.ArgumentParser(
        description="Jalankan program Pusingcuk."
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--fmt", action="store_true", help="Rapikan indentasi berkas sumber")
    modes.add_argument("--check", action="store_true", help="Periksa sintaks tanpa menjalankan program")
    parser.add_argument("file", nargs="?", help="Berkas sumber .cuk (atau .pusingcuk untuk kompatibilitas)")
    args = parser.parse_args()
    if not args.file:
        parser.error("berkas sumber wajib diisi (gunakan --help untuk petunjuk)")
    path = Path(args.file)

    if args.fmt:
        if not path.is_file():
            print(f"Kesalahan: berkas tidak ditemukan: {path}", file=sys.stderr)
            return 3
        try:
            from tools.formatter import format_file
            format_file(path)
        except (OSError, UnicodeError, ValueError, SyntaxError) as exc:
            print(f"Kesalahan format: {exc}", file=sys.stderr)
            return 1
        print(f"Format selesai: {path}")
        return 0

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

    if args.check:
        try:
            parse_source(source, filename=str(path))
        except ParserError as exc:
            print(f"Kesalahan sintaks: {exc}", file=sys.stderr)
            return 2
        print(f"OK: sintaks valid — {path}")
        return 0

    try:
        run(source, source_path=path, project_root=path.resolve().parent)
    except ParserError as exc:
        print(f"Kesalahan sintaks: {exc}", file=sys.stderr)
        return 2
    except (RuntimeError, ValueError, TypeError, IndexError, OSError) as exc:
        print(f"Kesalahan runtime: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
