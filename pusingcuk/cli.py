#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

def cmd_compile(args):
    from compiler.bytecode import compile_source
    src = Path(args.file).read_text(encoding="utf-8")
    artifact = compile_source(src, args.file)
    Path(args.output).write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"compiled {args.file} -> {args.output} ({len(artifact['functions'])} funcs)")

def main():
    p = argparse.ArgumentParser(prog="pusingcuk")
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("compile")
    c.add_argument("file")
    c.add_argument("-o", "--output", required=True)
    c.set_defaults(func=cmd_compile)
    args = p.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
