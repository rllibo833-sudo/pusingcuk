"""Self-hosted .cuk frontend bridge for the currently implemented statement subset.

The lexer/parser grammar lives in examples/self_hosting/source_lexer.cuk.
It emits AST JSON, which is wrapped in canonical, validated IR v1 for existing backends.
"""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from compiler.ir import FORMAT, IR_VERSION, LANGUAGE_VERSION, _collect_node_locations, _features, validate

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SOURCE = ROOT / "examples" / "self_hosting" / "source_lexer.cuk"
MARKER = "lah contoh = "

class SelfHostedFrontendError(ValueError):
    """The .cuk frontend rejected input or failed to emit its AST."""



def _frontend_script(source: str) -> str:
    if not isinstance(source, str) or not source.strip():
        raise SelfHostedFrontendError("source kosong")
    if "\x00" in source:
        raise SelfHostedFrontendError("source mengandung NUL")
    original = FRONTEND_SOURCE.read_text(encoding="utf-8")
    if MARKER not in original:
        raise SelfHostedFrontendError(f"marker frontend tidak ditemukan: {MARKER!r}")
    prefix = original.split(MARKER, 1)[0]
    return (
        prefix + "\nlah source_input = " + json.dumps(source, ensure_ascii=False)
        + '\nlah hasil_parse = parse_program(pindai(source_input))'
        + '\nnjir hasil_parse["status"] != "OK"'
        + '\n    hedeh "SELFHOST_PARSE_ERROR"'
        + '\nkampret'
        + '\n    hedeh ir_program(hasil_parse["node"])'
        + '\nselesai njir\nselesai jancuk\n'
    )

def from_source(source: str, source_name: str = "<memory>") -> dict:
    """Parse a supported source subset in .cuk, then validate canonical IR v1."""
    if not isinstance(source_name, str) or not source_name:
        raise ValueError("source_name tidak boleh kosong")
    # The staged parser handles statements, not the outer program delimiters.
    # Normalize those delimiters before passing source into the .cuk parser.
    source = "\n".join(line for line in source.splitlines() if line.strip() not in {"jancuk", "selesai jancuk"})
    script = _frontend_script(source)
    with tempfile.TemporaryDirectory(prefix=".cuk-selfhost-", dir=ROOT) as tmp:
        path = Path(tmp) / "frontend_input.cuk"
        path.write_text(script, encoding="utf-8")
        run = subprocess.run(
            [sys.executable, str(ROOT / "pusingcuk_new.py"), str(path)], cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, check=False,
        )
    if run.returncode != 0:
        raise SelfHostedFrontendError(run.stderr.strip() or "frontend .cuk gagal dijalankan")
    output = run.stdout.strip().splitlines()
    if not output or output[-1] == "SELFHOST_PARSE_ERROR":
        raise SelfHostedFrontendError("frontend .cuk menolak sintaks source")
    try:
        program = json.loads(output[-1])
    except json.JSONDecodeError as exc:
        raise SelfHostedFrontendError("frontend .cuk menghasilkan AST bukan JSON valid") from exc
    if not isinstance(program, dict) or program.get("kind") != "Program":
        raise SelfHostedFrontendError("frontend .cuk tidak menghasilkan node Program")
    document = {
        "format": FORMAT, "ir_version": IR_VERSION, "language_version": LANGUAGE_VERSION,
        "source_name": Path(source_name.replace(chr(92), "/")).name if source_name != "<memory>" else source_name,
        "features": _features(program), "source_map": _collect_node_locations(program), "program": program,
    }
    validate(document)
    return document
