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
        if args.fmt or args.check:
            parser.error("--fmt dan --check membutuhkan berkas sumber")
        from terminal import main as repl_main
        return repl_main()
    input_path = Path(args.file).expanduser()
    path = input_path.resolve()
    cwd = Path.cwd().resolve()
    if input_path.is_absolute():
        project_root = path.parent
    else:
        try:
            path.relative_to(cwd)
            project_root = cwd
        except ValueError:
            project_root = path.parent

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
            message = str(exc)
            if "Kesalahan sintaks:" not in message and "Kesalahan lexer:" not in message:
                message = f"Kesalahan sintaks: {message}"
            print(message, file=sys.stderr)
            return 2
        print(f"OK: sintaks valid — {path}")
        return 0

    try:
        run(source, source_path=path, project_root=project_root)
    except ParserError as exc:
        message = str(exc)
        if "Kesalahan sintaks:" not in message and "Kesalahan lexer:" not in message:
            message = f"Kesalahan sintaks: {message}"
        print(message, file=sys.stderr)
        return 2
    except (RuntimeError, ValueError, TypeError, IndexError, OSError, ArithmeticError, KeyError) as exc:
        print(f"Kesalahan runtime: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
