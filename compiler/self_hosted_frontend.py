"""Run the .cuk-authored frontend and validate its emitted canonical IR v1 artifact.

The .cuk source owns tokenization, parsing, AST construction, and IR serialization.
Python hosts execution of the trusted compiler source and validates the emitted IR;
it never parses the user's source program as a fallback.
"""
from __future__ import annotations

import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import tempfile
from pathlib import Path

from compiler.ir import validate
from evaluator import Evaluator

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SOURCE = ROOT / "examples" / "self_hosting" / "compiler.cuk"
MARKER = "lah contoh = "
# These larger limits apply only while running the checked-in compiler frontend.
# Regular .cuk programs keep the language's default execution limits.
FRONTEND_MAX_STEPS = 10_000_000
FRONTEND_MAX_LOOP_ITERATIONS = 250_000
FRONTEND_MAX_INTERMEDIATE_SIZE = 8 * 1024 * 1024
MAX_SOURCE_BYTES = 256_000


class SelfHostedFrontendError(ValueError):
    """The .cuk frontend rejected input or failed to emit its AST."""


def _frontend_prefix() -> str:
    original = FRONTEND_SOURCE.read_text(encoding="utf-8")
    if MARKER not in original:
        raise SelfHostedFrontendError(f"marker frontend tidak ditemukan: {MARKER!r}")
    return original.split(MARKER, 1)[0]


def frontend_driver_script() -> str:
    """Return a reusable .cuk frontend that reads a JSON source payload from stdin."""
    return _frontend_prefix() + '''
tanya input_payload_json = ""
lah input_payload = jadi_json(input_payload_json)
njir input_payload == salah
    hedeh "SELFHOST_INPUT_ERROR"
kampret
    lah ir_source_name = input_payload["source_name"]
    lah source_input = input_payload["source"]
    lah hasil_parse = parse_program(pindai(source_input))
    njir hasil_parse["status"] != "OK"
        hedeh "SELFHOST_PARSE_ERROR:" + teks(hasil_parse["index"])
    kampret
        hedeh ir_document(hasil_parse["node"], ir_source_name)
    selesai njir
selesai njir
selesai jancuk
'''


def _frontend_script(source: str, source_name: str) -> str:
    if not isinstance(source, str) or not source.strip():
        raise SelfHostedFrontendError("source kosong")
    if "\x00" in source:
        raise SelfHostedFrontendError("source mengandung NUL")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise SelfHostedFrontendError(f"source melewati batas {MAX_SOURCE_BYTES} byte")
    prefix = _frontend_prefix()
    return (
        prefix + "\nlah ir_source_name = " + json.dumps(source_name, ensure_ascii=False)
        + "\nlah source_input = " + json.dumps(source, ensure_ascii=False)
        + '\nlah hasil_parse = parse_program(pindai(source_input))'
        + '\nnjir hasil_parse["status"] != "OK"'
        + '\n    hedeh "SELFHOST_PARSE_ERROR:" + teks(hasil_parse["index"])'
        + '\nkampret'
        + '\n    hedeh ir_document(hasil_parse["node"], ir_source_name)'
        + '\nselesai njir\nselesai jancuk\n'
    )


def from_source(source: str, source_name: str = "<memory>") -> dict:
    """Parse source in the .cuk frontend, then validate canonical IR v1."""
    if not isinstance(source_name, str) or not source_name:
        raise ValueError("source_name tidak boleh kosong")
    # No Python-reference-parser fallback: a syntax gap must fail visibly.
    source = "\n".join(line for line in source.splitlines() if line.strip() not in {"jancuk", "selesai jancuk"})
    normalized_name = Path(source_name.replace(chr(92), "/")).name if source_name != "<memory>" else source_name
    script = _frontend_script(source, normalized_name)
    stdout, stderr = StringIO(), StringIO()
    with tempfile.TemporaryDirectory(prefix=".cuk-selfhost-", dir=ROOT) as tmp:
        path = Path(tmp) / "frontend_input.cuk"
        path.write_text(script, encoding="utf-8")
        host = Evaluator(
            source_path=path,
            project_root=ROOT,
            max_steps=FRONTEND_MAX_STEPS,
            max_loop_iterations=FRONTEND_MAX_LOOP_ITERATIONS,
            max_intermediate_size=FRONTEND_MAX_INTERMEDIATE_SIZE,
        )
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                host.run(script)
        except Exception as exc:
            detail = str(exc).strip() or stderr.getvalue().strip() or "frontend .cuk gagal dijalankan"
            raise SelfHostedFrontendError(detail) from exc
    output = stdout.getvalue().strip().splitlines()
    if not output or output[-1].startswith("SELFHOST_PARSE_ERROR:"):
        token_index = output[-1].partition(":")[2] if output else "unknown"
        raise SelfHostedFrontendError(
            f"frontend .cuk menolak sintaks source pada token index {token_index}"
        )
    try:
        document = json.loads(output[-1])
    except json.JSONDecodeError as exc:
        raise SelfHostedFrontendError("frontend .cuk menghasilkan IR bukan JSON valid") from exc
    if not isinstance(document, dict) or not isinstance(document.get("program"), dict) or document["program"].get("kind") != "Program":
        raise SelfHostedFrontendError("frontend .cuk tidak menghasilkan dokumen IR v1")
    validate(document)
    return document
