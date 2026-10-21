"""Reproducible two-stage build check for the currently supported self-hosted subset.

This is deliberately not advertised as full self-hosting: both stages currently
run on the Python host. The command makes stage artifacts and rejects drift,
so the project has an executable bootstrap gate rather than a documentation claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from compiler.bytecode import compile_ir
from compiler.ir import dumps
from compiler.self_hosted_frontend import SelfHostedFrontendError, from_source
from compiler.vm import VirtualMachine, VMError

ROOT = Path(__file__).resolve().parents[1]
MAX_SOURCE_BYTES = 1_048_576


class BootstrapError(ValueError):
    """The staged build is invalid or non-reproducible."""


def _read(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise BootstrapError(f"cannot read source: {exc}") from exc
    if len(raw) > MAX_SOURCE_BYTES:
        raise BootstrapError(f"source exceeds {MAX_SOURCE_BYTES} bytes")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BootstrapError("source must be valid UTF-8") from exc


def _artifact(document: dict, bytecode: dict, source_name: str) -> dict:
    ir_bytes = dumps(document).encode("utf-8")
    bytecode_bytes = (
        json.dumps(bytecode, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    output = __import__("io").StringIO()
    VirtualMachine(bytecode, output_stream=output).run()
    return {
        "ir": ir_bytes,
        "bytecode": bytecode_bytes,
        "stdout": output.getvalue().encode("utf-8"),
        "source_name": source_name,
    }


def build(source: str, source_name: str) -> dict:
    """Run stage 1 and stage 2 and require byte-for-byte reproducible artifacts."""
    if not isinstance(source, str) or not source.strip():
        raise BootstrapError("source is empty")
    if "\x00" in source:
        raise BootstrapError("source contains NUL")

    stages = []
    try:
        for stage in (1, 2):
            document = from_source(source, source_name)
            bytecode = compile_ir(document)
            stages.append(_artifact(document, bytecode, source_name))
    except (SelfHostedFrontendError, VMError, ValueError, TypeError, KeyError, RecursionError) as exc:
        raise BootstrapError(f"stage failed: {exc}") from exc

    for key in ("ir", "bytecode", "stdout"):
        if stages[0][key] != stages[1][key]:
            raise BootstrapError(f"stage 1/2 mismatch: {key}")

    return {
        "schema": "pusingcuk-bootstrap-evidence",
        "schema_version": 1,
        "status": "reproducible-subset",
        "full_self_hosting": False,
        "source_name": source_name,
        "stages": [
            {
                "stage": index,
                "ir_sha256": hashlib.sha256(item["ir"]).hexdigest(),
                "bytecode_sha256": hashlib.sha256(item["bytecode"]).hexdigest(),
                "stdout_sha256": hashlib.sha256(item["stdout"]).hexdigest(),
                "stdout": item["stdout"].decode("utf-8"),
            }
            for index, item in enumerate(stages, start=1)
        ],
        "comparison": "identical",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify deterministic stage-1/stage-2 builds for the supported .cuk frontend subset."
    )
    parser.add_argument("source", help=".cuk source file")
    parser.add_argument("--evidence", metavar="FILE", help="write machine-readable build evidence")
    args = parser.parse_args(argv)
    try:
        source_path = Path(args.source)
        evidence = build(_read(source_path), source_path.name)
        encoded = json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.evidence:
            destination = Path(args.evidence)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(encoded, encoding="utf-8")
        print("BOOTSTRAP_SUBSET_OK: stage 1 and stage 2 artifacts are identical")
        print(f"full_self_hosting={str(evidence['full_self_hosting']).lower()}")
        print(f"bytecode_sha256={evidence['stages'][0]['bytecode_sha256']}")
        if args.evidence:
            print(f"evidence={args.evidence}")
        return 0
    except (BootstrapError, OSError) as exc:
        print(f"BOOTSTRAP_SUBSET_FAILED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
