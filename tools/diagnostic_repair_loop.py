"""Deterministic, import-safe source diagnostics for PusingCuk.

This helper only lexes and parses untrusted source. It does not execute it,
write generated proposals, or apply repairs automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from lexer import Lexer, LexerError
from parser import Parser, ParserError

ROOT = Path(__file__).resolve().parents[1]
_ALLOWED_SUFFIXES = {".cuk", ".pusingcuk"}


def _diagnostic(message: str) -> dict[str, Any]:
    match = re.search(r"(?:Baris|baris)\s+(\d+)", message)
    line = int(match.group(1)) if match else 0
    return {
        "line": line,
        "msg": message,
        "hint": "Periksa sintaks pada baris yang dilaporkan; helper ini tidak menjalankan kode.",
    }


def _response(
    *,
    ok: bool,
    status: str,
    code: str,
    source_path: str,
    source: str = "",
    source_sha256: str = "",
    result: Any = None,
    diagnostics: list[dict[str, Any]] | None = None,
    automatic_apply: bool = False,
) -> dict[str, Any]:
    diagnostics = diagnostics or []
    return {
        "ok": ok,
        "status": status,
        "code": code,
        "result": result,
        "diagnostic": diagnostics,
        "source_path": source_path,
        "source_sha256": source_sha256,
        "repair": {"automatic_apply": automatic_apply},
        "ai_handoff": {
            "mode": "proposal_only",
            "source": source,
            "source_path": source_path,
            "diagnostic": diagnostics,
        },
    }


def run_case(source_path: str | Path, expected_output: list[str] | str | None = None) -> dict[str, Any]:
    """Return one stable JSON-compatible diagnostic result without import side effects."""
    supplied = Path(source_path)
    candidate = supplied if supplied.is_absolute() else ROOT / supplied
    candidate = candidate.resolve()
    try:
        relative = candidate.relative_to(ROOT)
    except ValueError:
        return _response(
            ok=False, status="failed", code="SOURCE_OUTSIDE_REPOSITORY",
            source_path=str(candidate),
            diagnostics=[_diagnostic("SOURCE_OUTSIDE_REPOSITORY: source berada di luar repository.")],
        )

    relative_text = relative.as_posix()
    if candidate.suffix not in _ALLOWED_SUFFIXES:
        return _response(
            ok=False, status="failed", code="SOURCE_NOT_CUK",
            source_path=relative_text,
            diagnostics=[_diagnostic("SOURCE_NOT_CUK: hanya berkas .cuk atau .pusingcuk yang diterima.")],
        )
    if not candidate.is_file():
        return _response(
            ok=False, status="failed", code="SOURCE_NOT_FOUND",
            source_path=relative_text,
            diagnostics=[_diagnostic("SOURCE_NOT_FOUND: berkas sumber tidak ditemukan.")],
        )

    try:
        source = candidate.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return _response(
            ok=False, status="failed", code="SOURCE_READ_ERROR",
            source_path=relative_text,
            diagnostics=[_diagnostic(f"SOURCE_READ_ERROR: {type(exc).__name__}.")],
        )

    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    if expected_output is not None:
        message = (
            "OUTPUT_MISMATCH: pemeriksaan expected-output memerlukan runtime terisolasi; "
            "hasil harus ditinjau manual. Helper ini hanya memvalidasi lexer dan parser."
        )
        return _response(
            ok=False, status="failed", code="OUTPUT_MISMATCH",
            source_path=relative_text, source=source, source_sha256=digest,
            diagnostics=[_diagnostic(message)], automatic_apply=False,
        )

    try:
        tokens = Lexer(source).tokenize()
        tree = Parser(tokens).parse()
    except (LexerError, ParserError, SyntaxError, ValueError) as exc:
        diagnostic = _diagnostic(str(exc))
        return _response(
            ok=False, status="failed", code="SYNTAX_ERROR",
            source_path=relative_text, source=source, source_sha256=digest,
            diagnostics=[diagnostic], automatic_apply=False,
        )

    return _response(
        ok=True, status="passed", code="OK",
        source_path=relative_text, source=source, source_sha256=digest,
        result={"tokens": len(tokens), "ast_kind": getattr(tree, "kind", None)},
        diagnostics=[], automatic_apply=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validasi lexer/parser .cuk tanpa mengeksekusi sumber.")
    parser.add_argument("source_path", help="Path sumber .cuk relatif terhadap repository atau path absolut di dalamnya")
    parser.add_argument("--json", action="store_true", help="Dipertahankan untuk kompatibilitas; output selalu JSON.")
    args = parser.parse_args(argv)
    result = run_case(args.source_path)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
