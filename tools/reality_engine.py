"""Fail-closed deterministic acceptance gate for PusingCuk proposals.

This module does not trust AI output. A proposal is accepted only when the
source is deterministic, reference/native execution agrees, all required
backends have passing evidence, and a relevant fixture is registered and verified.
Unavailable backends or missing fixture evidence cause rejection.
"""
from __future__ import annotations

import json
import math
import shutil
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
    """A process passes only on exit 0; expected output is checked separately."""
    try:
        proc = subprocess.run(
            command, cwd=ROOT, text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=TIMEOUT_SECONDS, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "FAIL", "matched": False, "error": "timeout", "exit_code": None, "stdout": "", "stderr": ""}
    except OSError as exc:
        return {"status": "UNAVAILABLE", "matched": False, "error": type(exc).__name__, "exit_code": None, "stdout": "", "stderr": ""}
    return {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "matched": False,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "stderr_class": classify_stderr(proc.returncode, proc.stderr),
        "source_line": source_line_from_stderr(proc.stderr),
    }


def _fixture_for_source(source: str, fixture_id: str | None = None) -> dict[str, Any] | None:
    """Resolve the fixture ID and exact source independently of runner evidence."""
    data = json.loads((ROOT / "tests" / "conformance" / "manifest.json").read_text(encoding="utf-8"))
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list):
        raise ValueError("fixture manifest has no fixtures list")
    ids = [item.get("id") for item in fixtures if isinstance(item, dict)]
    if len(ids) != len(fixtures) or len(ids) != len(set(ids)):
        raise ValueError("fixture manifest contains invalid or duplicate IDs")
    for fixture in fixtures:
        if fixture_id is not None and fixture.get("id") != fixture_id:
            continue
        name = fixture.get("source")
        if not isinstance(name, str) or Path(name).name != name:
            continue
        path = ROOT / "tests" / "conformance" / name
        try:
            canonical_source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        expected = fixture.get("expected")
        if (canonical_source.rstrip("\r\n") == source.rstrip("\r\n")
                and isinstance(expected, dict) and expected.get("exit_code") == 0
                and isinstance(expected.get("stdout"), str)):
            return fixture
    return None


def _check_output(result: dict[str, Any], expected: str) -> dict[str, Any]:
    ok = (result.get("status") == "PASS" and result.get("exit_code") == 0
          and result.get("stdout") == expected and result.get("stderr") == "")
    result["matched"] = ok
    if not ok and result.get("status") == "PASS":
        result["status"] = "FAIL"
        result["error"] = "output differs from manifest expected.stdout"
    return result


def _production_target_runner(source: str) -> dict[str, Any]:
    """Compile and execute a manifest-backed source for reference/native/JS/Python/VM."""
    fixture = _fixture_for_source(source)
    if fixture is None:
        return {
            "targets": {name: {"status": "FAIL", "matched": False,
                "error": "source has no exact successful fixture in canonical manifest",
                "exit_code": None, "stdout": "", "stderr": ""} for name in REQUIRED_TARGETS},
            "differential_ok": False, "regressions": [], "fixture_added": False, "fixture_reused": False, "fixture_id": None,
        }
    expected = fixture["expected"]["stdout"]
    source_path = ROOT / "tests" / "conformance" / fixture["source"]
    targets: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="cuk-reality-proposal-", dir=ROOT) as folder:
        work = Path(folder)
        targets["reference"] = _check_output(
            _run_command([sys.executable, str(ROOT / "pusingcuk_new.py"), str(source_path)], source_path), expected)
        native = work / "pusingcuk-native"
        built, error = build_native(native)
        if built:
            targets["native"] = _check_output(_run_command([str(native), str(source_path)], source_path), expected)
        else:
            targets["native"] = {"status": "UNAVAILABLE", "matched": False, "error": error or "native build unavailable",
                                 "exit_code": None, "stdout": "", "stderr": ""}
        specs = {
            "javascript": ("js", work / "proposal.js", "node"),
            "python": ("python", work / "proposal.py", "python"),
            "vm": ("vm", work / "proposal.bytecode.json", "vm"),
        }
        for target, (backend, artifact, runtime) in specs.items():
            if runtime == "node":
                executable = shutil.which("node")
                if not executable:
                    targets[target] = {"status": "UNAVAILABLE", "matched": False, "error": "Node.js executable not found",
                                       "exit_code": None, "stdout": "", "stderr": ""}
                    continue
                command = [executable, str(artifact)]
            elif runtime == "python":
                command = [sys.executable, str(artifact)]
            else:
                command = [sys.executable, "-m", "compiler.vm", str(artifact)]
            try:
                compiled = subprocess.run(
                    [sys.executable, "-m", "compiler", str(source_path), "--target", backend, "--output", str(artifact)],
                    cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                    capture_output=True, timeout=TIMEOUT_SECONDS, check=False)
            except subprocess.TimeoutExpired:
                targets[target] = {"status": "FAIL", "matched": False, "error": "compile timeout",
                                   "exit_code": None, "stdout": "", "stderr": ""}
                continue
            except OSError as exc:
                targets[target] = {"status": "UNAVAILABLE", "matched": False, "error": type(exc).__name__,
                                   "exit_code": None, "stdout": "", "stderr": ""}
                continue
            if compiled.returncode != 0 or not artifact.is_file():
                targets[target] = {"status": "FAIL", "matched": False,
                                   "error": "compiler rejected source or emitted no artifact",
                                   "exit_code": compiled.returncode, "stdout": "", "stderr": compiled.stderr}
                continue
            targets[target] = _check_output(_run_command(command, source_path), expected)
    all_pass = all(targets[name].get("status") == "PASS" and targets[name].get("exit_code") == 0
                   and targets[name].get("matched") is True for name in REQUIRED_TARGETS)
    outputs = [targets[name].get("stdout") for name in REQUIRED_TARGETS]
    return {"targets": targets, "differential_ok": all_pass and len(set(outputs)) == 1 and outputs[0] == expected,
            "regressions": [], "fixture_added": False, "fixture_reused": True, "fixture_id": fixture["id"]}

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
    fixture_id = evidence.get("fixture_id")
    fixture = _fixture_for_source(source, fixture_id) if isinstance(fixture_id, str) else None
    expected_output = fixture.get("expected", {}).get("stdout") if fixture else None
    if fixture is None:
        diagnostics.append(_diag("FIXTURE_REQUIRED", "Fixture ID tidak terdaftar atau source tidak cocok dengan fixture kanonis."))
    for target in REQUIRED_TARGETS:
        result = targets.get(target)
        output_matches = (isinstance(result, dict) and fixture is not None
                          and result.get("exit_code") == 0 and result.get("stdout") == expected_output
                          and result.get("stderr", "") == "")
        if not isinstance(result, dict) or result.get("status") != "PASS" or result.get("matched") is not True or not output_matches:
            status = result.get("status", "MISSING") if isinstance(result, dict) else "MISSING"
            detail = result.get("error", "") if isinstance(result, dict) else ""
            diagnostics.append(_diag(
                "TARGET_GATE_FAILED",
                f"{target}: {status}" + (f" ({detail})" if detail else ""),
            ))

    outputs = [targets.get(name, {}).get("stdout") if isinstance(targets.get(name), dict) else None for name in REQUIRED_TARGETS]
    independently_differential_ok = (
        fixture is not None
        and all(isinstance(targets.get(name), dict) and targets[name].get("status") == "PASS"
                and targets[name].get("exit_code") == 0 and targets[name].get("stdout") == expected_output
                and targets[name].get("stderr", "") == "" for name in REQUIRED_TARGETS)
        and len(set(outputs)) == 1
    )
    fixture_added = evidence.get("fixture_added") is True
    fixture_reused = evidence.get("fixture_reused") is True
    if fixture is None or not (fixture_added or fixture_reused):
        if not any(item["code"] == "FIXTURE_REQUIRED" for item in diagnostics):
            diagnostics.append(_diag("FIXTURE_REQUIRED", "Proposal harus cocok dengan fixture kanonis yang terdaftar; fitur baru memerlukan fixture yang benar-benar ditambahkan."))
    if evidence.get("differential_ok") is not True or not independently_differential_ok or evidence.get("regressions") != []:
        diagnostics.append(_diag("DIFFERENTIAL_GATE_FAILED", "Matriks differential tidak lengkap, gagal, atau memiliki regresi."))

    accepted = not diagnostics
    return {
        "ok": accepted,
        "status": "passed" if accepted else "rejected",
        "accepted": accepted,
        "diagnostic": diagnostics,
        "targets": targets,
        "fixture_added": evidence.get("fixture_added") is True,
        "fixture_reused": evidence.get("fixture_reused") is True,
        "fixture_id": evidence.get("fixture_id"),
        "differential_ok": evidence.get("differential_ok") is True,
        "regressions": evidence.get("regressions", []),
    }
