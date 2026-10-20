"""CLI entry point for running or checking PusingCuk source files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from interpreter import run
from parser import parse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pusingcuk.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "check"):
        command = commands.add_parser(name)
        command.add_argument("file", help="path to a .cuk or .pusingcuk source file")
    args = parser.parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        print("berkas tidak ditemukan: " + str(path), file=sys.stderr)
        return 2
    try:
        source = path.read_text(encoding="utf-8")
        if args.command == "check":
            parse(source, filename=str(path))
            print("OK")
            return 0
        run(source, filename=str(path))
        return 0
    except (OSError, UnicodeError, SyntaxError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
