"""Compare Evaluator-hosted and bytecode-executed runs of the .cuk frontend.

The second path compiles a generic driver with the Python reference parser and
bytecode compiler, then executes the .cuk-authored lexer/parser in PusingCuk's
bytecode VM. It checks IR, target bytecode, and output parity; it deliberately
does not claim full self-hosting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from functools import lru_cache
from io import StringIO
from pathlib import Path

from compiler.bytecode import compile_ir
from compiler.ir import dumps, from_source as reference_from_source, validate
from compiler.self_hosted_frontend import (
    SelfHostedFrontendError,
    frontend_driver_script,
    from_source,
)
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


def _artifact(
    document: dict,
    bytecode: dict,
    source_name: str,
    frontend_runtime: str,
    frontend_bytecode_sha256: str | None = None,
) -> dict:
    ir_bytes = dumps(document).encode("utf-8")
    bytecode_bytes = (
        json.dumps(bytecode, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    output = StringIO()
    VirtualMachine(bytecode, output_stream=output).run()
    return {
        "ir": ir_bytes,
        "bytecode": bytecode_bytes,
        "stdout": output.getvalue().encode("utf-8"),
        "source_name": source_name,
        "frontend_runtime": frontend_runtime,
        "frontend_bytecode_sha256": frontend_bytecode_sha256,
    }


@lru_cache(maxsize=1)
def _compiled_frontend_driver() -> tuple[dict, bytes]:
    """Compile the fixed .cuk frontend driver once per bootstrap process."""
    driver_ir = reference_from_source(frontend_driver_script(), "bootstrap_frontend.cuk")
    driver_bytecode = compile_ir(driver_ir)
    driver_bytes = (
        json.dumps(driver_bytecode, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    return driver_bytecode, driver_bytes


def _compiled_frontend_document(source: str, source_name: str) -> tuple[dict, bytes]:
    """Run the .cuk frontend as compiled bytecode instead of through Evaluator."""
    normalized_source = "\n".join(
        line for line in source.splitlines()
        if line.strip() not in {"jancuk", "selesai jancuk"}
    )
    normalized_name = (
        Path(source_name.replace(chr(92), "/")).name
        if source_name != "<memory>" else source_name
    )
    driver_bytecode, driver_bytes = _compiled_frontend_driver()
    payload = json.dumps(
        {"source_name": normalized_name, "source": normalized_source},
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n"
    output = StringIO()
    VirtualMachine(
        driver_bytecode,
        input_stream=StringIO(payload),
        output_stream=output,
        max_steps=10_000_000,
    ).run()
    lines = output.getvalue().splitlines()
    if not lines:
        raise BootstrapError("compiled .cuk frontend produced no output")
    emitted = lines[-1]
    if emitted == "SELFHOST_INPUT_ERROR":
        raise BootstrapError("compiled .cuk frontend rejected its JSON input payload")
    if emitted.startswith("SELFHOST_PARSE_ERROR:"):
        token_index = emitted.partition(":")[2] or "unknown"
        raise BootstrapError(f"compiled .cuk frontend rejected source at token index {token_index}")
    try:
        document = json.loads(emitted)
    except json.JSONDecodeError as exc:
        raise BootstrapError("compiled .cuk frontend emitted invalid IR JSON") from exc
    validate(document)
    return document, driver_bytes


def build(source: str, source_name: str) -> dict:
    """Compare Evaluator-hosted and bytecode-executed runs of the .cuk frontend."""
    if not isinstance(source, str) or not source.strip():
        raise BootstrapError("source is empty")
    if "\x00" in source:
        raise BootstrapError("source contains NUL")

    stages = []
    try:
        evaluator_document = from_source(source, source_name)
        bytecode_document, frontend_bytecode = _compiled_frontend_document(source, source_name)
        if dumps(evaluator_document) != dumps(bytecode_document):
            raise BootstrapError("stage 1/2 mismatch: frontend IR")
        stage_inputs = (
            (evaluator_document, "python-evaluator", None),
            (
                bytecode_document,
                "pusingcuk-bytecode-vm",
                hashlib.sha256(frontend_bytecode).hexdigest(),
            ),
        )
        for document, runtime, driver_hash in stage_inputs:
            bytecode = compile_ir(document)
            stages.append(_artifact(document, bytecode, source_name, runtime, driver_hash))
    except BootstrapError:
        raise
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
        "stage_strategy": "evaluator-vs-compiled-frontend-bytecode",
        "source_name": source_name,
        "stages": [
            {
                "stage": index,
                "frontend_runtime": item["frontend_runtime"],
                "frontend_bytecode_sha256": item["frontend_bytecode_sha256"],
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
