"""Fail-closed deterministic acceptance gate for PusingCuk proposals.

This module does not trust AI output. A proposal is accepted only when the
source is deterministic, reference/native execution agrees, all required
backends have passing evidence, and a relevant fixture has been added.
Unavailable backends or missing fixture evidence cause rejection.
"""
from __future__ import annotations

import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from lexer import Lexer
from parser import Parser
from tools.conformance import build_native, classify_stderr, source_line_from_stderr

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT_SECONDS = 5
REQUIRED_TARGETS = ("reference", "native", "javascript", "python", "vm")
NONDETERMINISTIC_CALLS = {
    "jam", "tanggal", "tanya", "kepo_internet", "kirim_api",
    "tulis", "baca", "tulis_json", "baca_json", "eksekusi", "angkut",
}


def _diag(code: str, message: str, line: int = 0, hint: str = "") -> dict[str, Any]:
    return {
        "line": int(line),
        "code": code,
        "msg": message,
        "hint": hint or "Proposal ditolak secara fail-closed; perbaiki penyebabnya lalu validasi ulang.",
    }


def _is_nondeterministic(tokens) -> str | None:
    for index, token in enumerate(tokens):
        if token.value == "tanya":
            return "tanya membaca input eksternal dan tidak deterministik."
        if token.value in NONDETERMINISTIC_CALLS:
            next_token = tokens[index + 1] if index + 1 < len(tokens) else None
            if next_token is not None and next_token.value == "(":
                return f"pemanggilan {token.value}() memiliki efek eksternal atau waktu yang tidak deterministik."
    return None


def _run_command(command: list[str], source_path: Path) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            command, cwd=ROOT, text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=TIMEOUT_SECONDS, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "FAIL", "matched": False, "error": "timeout"}
    except OSError as exc:
        return {"status": "UNAVAILABLE", "matched": False, "error": type(exc).__name__}
    return {
        "status": "PASS" if proc.returncode in (0, 1, 2, 3) else "FAIL",
        "matched": True,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr_class": classify_stderr(proc.returncode, proc.stderr),
        "source_line": source_line_from_stderr(proc.stderr),
    }


def _production_target_runner(source: str) -> dict[str, Any]:
    target_results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="cuk-reality-proposal-") as directory:
        source_path = Path(directory) / "proposal.cuk"
        source_path.write_text(source, encoding="utf-8")
        reference = _run_command(
            [sys.executable, str(ROOT / "pusingcuk_new.py"), str(source_path)], source_path
        )
        target_results["reference"] = reference

        native_binary = Path(directory) / "pusingcuk-native"
        native_ok, native_error = build_native(native_binary)
        if native_ok:
            target_results["native"] = _run_command([str(native_binary), str(source_path)], source_path)
        else:
            target_results["native"] = {
                "status": "UNAVAILABLE", "matched": False, "error": native_error or "native build unavailable"
            }

        # These targets are deliberately not marked as passing until the matrix
        # can compile and execute the same proposal for each backend.
        for target in ("javascript", "python", "vm"):
            target_results[target] = {
                "status": "UNAVAILABLE",
                "matched": False,
                "error": "target-specific proposal runner is not integrated",
            }

        differential_ok = (
            reference.get("status") == "PASS"
            and target_results["native"].get("status") == "PASS"
            and reference.get("exit_code") == target_results["native"].get("exit_code")
            and reference.get("stdout") == target_results["native"].get("stdout")
            and reference.get("stderr_class") == target_results["native"].get("stderr_class")
            and reference.get("source_line") == target_results["native"].get("source_line")
        )
    return {
        "targets": target_results,
        "differential_ok": differential_ok,
        "regressions": [],
        "fixture_added": False,
        "fixture_id": None,
    }


def validate_deterministic(
    source: str,
    *,
    target_runner: Callable[[str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate source and required target evidence; reject missing evidence."""
    diagnostics: list[dict[str, Any]] = []
    if not isinstance(source, str) or not source.strip():
        diagnostics.append(_diag("EMPTY_SOURCE", "Proposal harus berupa teks .cuk non-kosong."))
        return {"ok": False, "status": "rejected", "accepted": False, "diagnostic": diagnostics, "targets": {}}

    try:
        tokens = Lexer(source).tokenize()
        Parser(tokens).parse()
    except Exception as exc:
        diagnostics.append(_diag("SYNTAX_ERROR", str(exc)))
        return {"ok": False, "status": "rejected", "accepted": False, "diagnostic": diagnostics, "targets": {}}

    nondeterministic = _is_nondeterministic(tokens)
    if nondeterministic:
        diagnostics.append(_diag("NON_DETERMINISTIC", nondeterministic))
        return {"ok": False, "status": "rejected", "accepted": False, "diagnostic": diagnostics, "targets": {}}

    try:
        evidence = (target_runner or _production_target_runner)(source)
    except Exception as exc:
        diagnostics.append(_diag("VALIDATOR_ERROR", f"{type(exc).__name__}: {exc}"))
        return {"ok": False, "status": "rejected", "accepted": False, "diagnostic": diagnostics, "targets": {}}

    targets = evidence.get("targets", {})
    for target in REQUIRED_TARGETS:
        result = targets.get(target)
        if not isinstance(result, dict) or result.get("status") != "PASS" or result.get("matched") is not True:
            status = result.get("status", "MISSING") if isinstance(result, dict) else "MISSING"
            detail = result.get("error", "") if isinstance(result, dict) else ""
            diagnostics.append(_diag(
                "TARGET_GATE_FAILED",
                f"{target}: {status}" + (f" ({detail})" if detail else ""),
            ))

    if evidence.get("fixture_added") is not True or not evidence.get("fixture_id"):
        diagnostics.append(_diag("FIXTURE_REQUIRED", "Proposal belum memiliki fixture regresi relevan yang ditambahkan dan diverifikasi."))
    if evidence.get("differential_ok") is not True or evidence.get("regressions") != []:
        diagnostics.append(_diag("DIFFERENTIAL_GATE_FAILED", "Matriks differential tidak lengkap, gagal, atau memiliki regresi."))

    accepted = not diagnostics
    return {
        "ok": accepted,
        "status": "passed" if accepted else "rejected",
        "accepted": accepted,
        "diagnostic": diagnostics,
        "targets": targets,
        "fixture_added": evidence.get("fixture_added") is True,
        "fixture_id": evidence.get("fixture_id"),
        "differential_ok": evidence.get("differential_ok") is True,
        "regressions": evidence.get("regressions", []),
    }
