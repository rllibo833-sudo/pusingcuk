"""Runnable staged .cuk frontend -> canonical IR v1 -> bytecode -> VM pipeline.

The frontend grammar is intentionally a documented subset; this driver never
silently falls back to the Python parser when the .cuk frontend rejects input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from compiler.bytecode import compile_ir
from compiler.ir import dumps
from compiler.self_hosted_frontend import SelfHostedFrontendError, from_source
from compiler.vm import VirtualMachine, VMError


MAX_SOURCE_BYTES = 1 * 1024 * 1024


def compile_file(path: Path) -> tuple[dict, dict]:
    """Compile source using the .cuk lexer/parser, canonical IR, and VM bytecode."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"tidak dapat membaca sumber: {exc}") from exc
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError(f"sumber melewati batas {MAX_SOURCE_BYTES} byte")
    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("sumber harus UTF-8 valid") from exc
    document = from_source(source, path.name)
    return document, compile_ir(document)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Jalankan pipeline frontend .cuk -> IR v1 -> bytecode VM (subset self-hosted)."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--emit-ir", metavar="FILE", help="tulis IR v1 kanonis ke FILE")
    mode.add_argument("--emit-bytecode", metavar="FILE", help="tulis bytecode VM ke FILE")
    mode.add_argument("--check", action="store_true", help="kompilasi tanpa menjalankan program")
    parser.add_argument("source", help="berkas sumber .cuk")
    args = parser.parse_args(argv)

    source_path = Path(args.source)
    try:
        document, bytecode = compile_file(source_path)
        if args.emit_ir:
            Path(args.emit_ir).write_text(dumps(document), encoding="utf-8")
            print(f"IR v{document['ir_version']} ditulis: {args.emit_ir}")
        elif args.emit_bytecode:
            Path(args.emit_bytecode).write_text(
                json.dumps(bytecode, ensure_ascii=False, sort_keys=True, indent=2) + "\\n",
                encoding="utf-8",
            )
            print(f"Bytecode v{bytecode['bytecode_version']} ditulis: {args.emit_bytecode}")
        elif args.check:
            print(f"OK: frontend .cuk -> IR v{document['ir_version']} -> bytecode v{bytecode['bytecode_version']}")
        else:
            VirtualMachine(bytecode).run()
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError, SelfHostedFrontendError, VMError) as exc:
        print(f"Kesalahan compiler .cuk: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
