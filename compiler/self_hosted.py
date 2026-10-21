"""Runnable staged .cuk frontend -> canonical IR v1 -> bytecode -> VM pipeline.

The default path uses the .cuk frontend subset. Explicit --target compatibility
outputs use the canonical reference frontend and existing production backends;
they are intentionally not counted as proof of self-hosted bootstrap.
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


def _read_source(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"tidak dapat membaca sumber: {exc}") from exc
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError(f"sumber melewati batas {MAX_SOURCE_BYTES} byte")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("sumber harus UTF-8 valid") from exc


def compile_file(path: Path) -> tuple[dict, dict]:
    """Compile using the .cuk lexer/parser subset, canonical IR, and VM bytecode."""
    document = from_source(_read_source(path), path.name)
    return document, compile_ir(document)


def _compile_target(path: Path, target: str, output: Path) -> int:
    """Compatibility entrypoint consumed by the Reality Engine's target runner."""
    from compiler.ir import from_source as reference_from_source

    source = _read_source(path)
    document = reference_from_source(source, path.name)
    if target == "vm":
        artifact = compile_ir(document)
        output.write_text(json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    elif target == "js":
        from compiler.js_backend import generate
        output.write_text(generate(document), encoding="utf-8")
    elif target == "python":
        from compiler.python_backend import generate
        output.write_text(generate(document), encoding="utf-8")
    elif target == "go":
        from compiler.go_backend import generate
        output.write_text(generate(document), encoding="utf-8")
    elif target == "html":
        from compiler.html_backend import generate
        output.write_text(generate(document), encoding="utf-8")
    else:
        raise ValueError(f"target tidak didukung: {target}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline frontend .cuk -> IR v1 -> bytecode VM; target compatibility mode uses canonical reference frontend."
    )
    parser.add_argument("source", help="berkas sumber .cuk")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--emit-ir", metavar="FILE", help="tulis IR v1 kanonis ke FILE")
    mode.add_argument("--emit-bytecode", metavar="FILE", help="tulis bytecode VM ke FILE")
    mode.add_argument("--check", action="store_true", help="kompilasi tanpa menjalankan program")
    parser.add_argument("--target", choices=("js", "python", "vm", "go", "html"), help="target kompatibilitas untuk runner Reality Engine")
    parser.add_argument("-o", "--output", help="berkas keluaran target")
    args = parser.parse_args(argv)

    source_path = Path(args.source)
    try:
        if args.target:
            if not args.output:
                parser.error("--target memerlukan --output")
            return _compile_target(source_path, args.target, Path(args.output))
        if args.output:
            parser.error("--output hanya berlaku bersama --target")
        document, bytecode = compile_file(source_path)
        if args.emit_ir:
            Path(args.emit_ir).write_text(dumps(document), encoding="utf-8")
            print(f"IR v{document['ir_version']} ditulis: {args.emit_ir}")
        elif args.emit_bytecode:
            Path(args.emit_bytecode).write_text(
                json.dumps(bytecode, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
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
