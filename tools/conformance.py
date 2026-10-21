#!/usr/bin/env python3
"""Run the manifest-driven Pusingcuk cross-runtime conformance suite."""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from library.builtin_contract import BUILTIN_CONTRACT  # validates metadata before fixtures run

FIXTURES = ROOT / "tests" / "conformance"
MANIFEST = FIXTURES / "manifest.json"
ALLOWED_RUNTIME_STATES = {"required", "optional", "unsupported"}
ALLOWED_EXPECTED_KEYS = {"exit_code", "stdout", "stderr_class", "stdin", "source_line"}
ALLOWED_FIXTURE_KEYS = {"id", "source", "profile", "requires", "expected", "runtimes"}


class ManifestError(ValueError):
    pass


def load_manifest():
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"manifest tidak dapat dibaca: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ManifestError("schema_version harus berupa angka 1")
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ManifestError("fixtures harus berupa daftar yang tidak kosong")

    seen_ids = set()
    validated = []
    for index, item in enumerate(fixtures):
        if not isinstance(item, dict) or set(item) - ALLOWED_FIXTURE_KEYS:
            raise ManifestError(f"fixture #{index + 1}: bentuk atau field tidak dikenal")
        fixture_id = item.get("id")
        if not isinstance(fixture_id, str) or not fixture_id.strip() or fixture_id in seen_ids:
            raise ManifestError(f"fixture #{index + 1}: id kosong atau duplikat")
        seen_ids.add(fixture_id)
        source = item.get("source")
        if not isinstance(source, str) or not source or Path(source).is_absolute():
            raise ManifestError(f"{fixture_id}: source harus path relatif")
        source_path = (FIXTURES / source).resolve()
        try:
            source_path.relative_to(FIXTURES.resolve())
        except ValueError as exc:
            raise ManifestError(f"{fixture_id}: path source keluar dari direktori fixture") from exc
        if not source_path.is_file() or source_path.suffix not in {".cuk", ".pusingcuk"}:
            raise ManifestError(f"{fixture_id}: source harus file .cuk atau .pusingcuk yang ada")

        expected = item.get("expected")
        if not isinstance(expected, dict) or set(expected) - ALLOWED_EXPECTED_KEYS:
            raise ManifestError(f"{fixture_id}: expected tidak valid")
        if not isinstance(expected.get("exit_code"), int) or isinstance(expected.get("exit_code"), bool):
            raise ManifestError(f"{fixture_id}: expected.exit_code harus integer")
        if not isinstance(expected.get("stdout"), str):
            raise ManifestError(f"{fixture_id}: expected.stdout harus teks")
        stderr_class = expected.get("stderr_class")
        if stderr_class not in (None, "syntax_error", "runtime_error"):
            raise ManifestError(
                f"{fixture_id}: stderr_class harus null, 'syntax_error', atau 'runtime_error'"
            )
        if stderr_class is None:
            if expected["exit_code"] != 0:
                raise ManifestError(f"{fixture_id}: kasus gagal wajib menetapkan stderr_class")
            if "source_line" in expected:
                raise ManifestError(f"{fixture_id}: kasus sukses tidak boleh memiliki source_line")
        else:
            expected_code = 2 if stderr_class == "syntax_error" else 1
            if expected["exit_code"] != expected_code:
                raise ManifestError(
                    f"{fixture_id}: {stderr_class} harus memakai exit code {expected_code}"
                )
            if expected.get("stdout") != "":
                raise ManifestError(f"{fixture_id}: fixture error harus mengharapkan stdout kosong")
            source_line = expected.get("source_line")
            if not isinstance(source_line, int) or isinstance(source_line, bool) or source_line < 1:
                raise ManifestError(f"{fixture_id}: fixture error wajib menetapkan source_line positif")
        if not isinstance(expected.get("stdin", ""), str):
            raise ManifestError(f"{fixture_id}: expected.stdin harus teks")

        runtimes = item.get("runtimes")
        if not isinstance(runtimes, dict) or not runtimes:
            raise ManifestError(f"{fixture_id}: runtimes harus berupa objek")
        for runtime, state in runtimes.items():
            if runtime not in {"reference", "native"}:
                raise ManifestError(f"{fixture_id}: runtime tidak dikenal: {runtime}")
            if not isinstance(state, str) or state not in ALLOWED_RUNTIME_STATES:
                raise ManifestError(f"{fixture_id}: status runtime tidak valid: {runtime}")
        validated.append((item, source_path))
    return validated


def classify_stderr(returncode, stderr):
    """Classify stable public error categories instead of matching full messages."""
    text = stderr.lstrip()
    if returncode == 0:
        return None if not text else "error"
    # Python diagnostics include a source location before the category label;
    # C diagnostics may begin directly with the category. Classify the first
    # diagnostic line, not just the first characters of stderr.
    header = text.splitlines()[0] if text else ""
    if "Kesalahan sintaks:" in header:
        return "syntax_error"
    if "Kesalahan runtime:" in header:
        return "runtime_error"
    return "error"


def source_line_from_stderr(stderr):
    """Return source line across C's and Python's diagnostic location formats."""
    match = re.search(r"\bBaris\s+(\d+)\b", stderr, flags=re.IGNORECASE)
    if match is None:
        # Python parser locations use [filename:line:column].
        match = re.search(r"\[[^\]\n]*:(\d+):\d+\]", stderr)
    return int(match.group(1)) if match else None


def source_column_from_stderr(stderr):
    """Return a source column when the runtime publishes one."""
    match = re.search(r"\bBaris\s+\d+\s*,\s*kolom\s+(\d+)\b", stderr, flags=re.IGNORECASE)
    if match is None:
        match = re.search(r"\[[^\]\n]*:\d+:(\d+)\]", stderr)
    return int(match.group(1)) if match else None


def classify_observation(returncode, stderr, run_error=None, matched=False):
    """Describe runtime behavior independently of fixture expectations."""
    if run_error == "timeout":
        return "harness_timeout"
    if run_error:
        return "harness_error"
    category = classify_stderr(returncode, stderr)
    if category == "syntax_error":
        return "syntax_error"
    if category == "runtime_error":
        return "runtime_failure"
    if category == "error" or returncode != 0:
        return "runtime_or_harness_error"
    return "none" if matched else "semantic_mismatch"


def repair_hint(category):
    """Stable Indonesian guidance without treating harness failures as source defects."""
    return {
        "none": "Fixture sesuai kontrak; jangan mengubah semantik tanpa kasus reproduksi baru.",
        "syntax_error": "Periksa lokasi sintaks dan cocokkan dengan SPEC.md; fixture negatif tetap valid jika penolakan ini memang diharapkan.",
        "runtime_failure": "Periksa pesan runtime dan baris sumber; reproduksi sebagai fixture sebelum mengubah evaluator atau native runtime.",
        "semantic_mismatch": "Bandingkan exit code, stdout, kelas diagnostik, dan lokasi aktual dengan manifest sebelum mengubah kontrak atau target.",
        "backend_unavailable": "Backend wajib tidak berhasil dibangun/dijalankan; perbaiki lingkungan backend, jangan menyebutnya kesalahan source.",
        "harness_timeout": "Fixture melewati batas waktu harness; periksa loop/kompleksitas dan timeout runner terlebih dahulu.",
        "harness_error": "Harness tidak dapat menjalankan fixture; periksa command, izin, dan lingkungan pengujian terlebih dahulu.",
        "runtime_or_harness_error": "Format diagnostik tidak dikenali; periksa stderr dan harness sebelum menyimpulkan bug source.",
    }.get(category, "Periksa bukti runtime aktual dan manifest fixture sebelum mengubah semantik.")


def run_command(command, stdin_text):
    try:
        result = subprocess.run(
            command,
            input=stdin_text,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            cwd=ROOT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"
    return result, None


def build_native(output_path):
    compiler = shlex.split(os.environ.get("CC", "cc"))
    if not compiler:
        return False, "variabel CC kosong"
    command = [
        *compiler, "-std=c11", "-O2", "-Wall", "-Wextra",
        "-DPUSINGCUK_VERSION=\"conformance\"",
        str(ROOT / "native" / "pusingcuk.c"), "-lm", "-o", str(output_path),
    ]
    try:
        result = subprocess.run(
            command, cwd=ROOT, text=True, encoding="utf-8",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    if result.returncode != 0:
        return False, result.stderr.strip() or "kompilasi native gagal"
    return True, ""



def evaluate_fixture(fixture_id):
    """Execute a registered fixture and return expected-vs-observed runtime evidence."""
    fixtures = load_manifest()
    selected = next(((item, path) for item, path in fixtures if item["id"] == fixture_id), None)
    if selected is None:
        return {
            "ok": False, "error": "CONFORMANCE_FIXTURE_NOT_FOUND",
            "fixture_id": fixture_id, "failure_category": "fixture_not_found",
            "repair_hint": "Pilih fixture_id yang tercantum pada tests/conformance/manifest.json.",
        }

    item, source_path = selected
    expected = item["expected"]
    runtime_results = {}
    native_states = item["runtimes"].get("native") in {"required", "optional"}
    with tempfile.TemporaryDirectory(prefix="pusingcuk-ai-fixture-") as temp:
        native_path = Path(temp) / "pusingcuk-native"
        native_ready, native_error = build_native(native_path) if native_states else (False, "")
        for runtime, state in item["runtimes"].items():
            if state == "unsupported":
                category = "backend_unavailable"
                runtime_results[runtime] = {
                    "status": "unsupported", "matched": False,
                    "observed_category": category, "diagnostic_location": None,
                    "repair_hint": repair_hint(category),
                }
                continue
            if runtime == "native" and not native_ready:
                category = "backend_unavailable"
                runtime_results[runtime] = {
                    "status": "unavailable", "matched": False,
                    "reason": native_error or "native runtime tidak diperlukan",
                    "observed_category": category, "diagnostic_location": None,
                    "repair_hint": repair_hint(category),
                }
                continue

            command = (
                [sys.executable, str(ROOT / "pusingcuk_new.py"), str(source_path)]
                if runtime == "reference"
                else [str(native_path), str(source_path)]
            )
            result, run_error = run_command(command, expected.get("stdin", ""))
            if run_error:
                category = classify_observation(None, "", run_error=run_error)
                runtime_results[runtime] = {
                    "status": run_error, "matched": False,
                    "observed_category": category, "diagnostic_location": None,
                    "repair_hint": repair_hint(category),
                }
                continue

            actual_class = classify_stderr(result.returncode, result.stderr)
            actual_line = source_line_from_stderr(result.stderr)
            actual_column = source_column_from_stderr(result.stderr)
            matched = (
                result.returncode == expected["exit_code"]
                and result.stdout == expected["stdout"]
                and actual_class == expected.get("stderr_class")
                and (
                    expected.get("source_line") is None
                    or actual_line == expected["source_line"]
                )
            )
            category = classify_observation(result.returncode, result.stderr, matched=matched)
            location = (
                {"line": actual_line, "column": actual_column}
                if actual_line is not None and actual_column is not None
                else ({"line": actual_line} if actual_line is not None else None)
            )
            runtime_results[runtime] = {
                "status": "passed" if matched else "failed",
                "matched": matched, "exit_code": result.returncode,
                "stdout": result.stdout[:2000], "stderr_class": actual_class,
                "source_line": actual_line, "source_column": actual_column,
                "diagnostic_location": location, "observed_category": category,
                "repair_hint": repair_hint(category), "stderr": result.stderr[:2000],
            }

    required = [runtime for runtime, state in item["runtimes"].items() if state == "required"]
    required_passed = all(runtime_results.get(runtime, {}).get("matched") is True for runtime in required)
    parity_claim = (
        item["runtimes"].get("reference") == "required"
        and item["runtimes"].get("native") == "required"
        and required_passed
    )
    if required_passed:
        failure_category = "none"
    else:
        categories = [
            runtime_results.get(runtime, {}).get("observed_category", "backend_unavailable")
            for runtime in required
            if runtime_results.get(runtime, {}).get("matched") is not True
        ]
        priority = (
            "backend_unavailable", "harness_timeout", "harness_error",
            "syntax_error", "runtime_failure", "semantic_mismatch", "runtime_or_harness_error",
        )
        failure_category = next(
            (candidate for candidate in priority if candidate in categories),
            categories[0] if categories else "runtime_or_harness_error",
        )
    return {
        "ok": required_passed, "operation": "conformance_check",
        "fixture_id": item["id"], "source": item["source"],
        "profile": item.get("profile"), "requires": item.get("requires", []),
        "expected": expected, "runtime_results": runtime_results,
        "required_runtimes_passed": required_passed,
        "python_native_parity_proven_for_fixture": parity_claim,
        "evidence_status": "RUNTIME_TERUJI" if required_passed else "RUNTIME_GAGAL",
        "failure_category": failure_category, "repair_hint": repair_hint(failure_category),
        "scope_note": (
            "Kategori observasi menggambarkan hasil aktual; fixture negatif dapat mengamati "
            "syntax_error/runtime_failure dan tetap lulus jika sesuai kontrak. Hanya fixture "
            "terdaftar yang dijalankan; ini bukan eksekusi source AI/pengguna atau sandbox."
        ),
    }

def main():
    try:
        fixtures = load_manifest()
    except ManifestError as exc:
        print(f"MANIFEST FAIL: {exc}", file=sys.stderr)
        return 2

    states = {"PASS": 0, "FAIL": 0, "UNSUPPORTED": 0}
    native_needed = any(
        item["runtimes"].get("native") in {"required", "optional"}
        for item, _ in fixtures
    )
    with tempfile.TemporaryDirectory(prefix="pusingcuk-conformance-") as temp:
        native_path = Path(temp) / "pusingcuk-native"
        native_ready, native_error = build_native(native_path) if native_needed else (False, "")

        for item, source_path in fixtures:
            expected = item["expected"]
            for runtime, state in item["runtimes"].items():
                label = f'{item["id"]} [{runtime}]'
                if state == "unsupported":
                    states["UNSUPPORTED"] += 1
                    print(f"UNSUPPORTED {label}: runtime belum mendukung fitur ini")
                    continue
                if runtime == "native" and not native_ready:
                    if state == "optional":
                        states["UNSUPPORTED"] += 1
                        print(f"UNSUPPORTED {label}: native tidak tersedia ({native_error})")
                    else:
                        states["FAIL"] += 1
                        print(f"FAIL {label}: native wajib tetapi build gagal ({native_error})")
                    continue

                command = (
                    [sys.executable, str(ROOT / "pusingcuk_new.py"), str(source_path)]
                    if runtime == "reference"
                    else [str(native_path), str(source_path)]
                )
                result, run_error = run_command(command, expected.get("stdin", ""))
                if run_error:
                    states["FAIL"] += 1
                    print(f"FAIL {label}: {run_error}")
                    continue

                actual_class = classify_stderr(result.returncode, result.stderr)
                expected_exit_code = expected["exit_code"]
                matches = (
                    result.returncode == expected_exit_code
                    and result.stdout == expected["stdout"]
                    and actual_class == expected.get("stderr_class")
                    and (
                        expected.get("source_line") is None
                        or source_line_from_stderr(result.stderr) == expected["source_line"]
                    )
                )
                if matches:
                    states["PASS"] += 1
                    print(f"PASS {label}")
                else:
                    states["FAIL"] += 1
                    print(f"FAIL {label}")
                    print(f"  exit: expected={expected_exit_code} actual={result.returncode}")
                    print(f"  stdout expected={expected['stdout']!r} actual={result.stdout!r}")
                    print(f"  stderr_class expected={expected.get('stderr_class')!r} actual={actual_class!r}")
                    if expected.get("source_line") is not None:
                        print(
                            "  source_line expected="
                            f"{expected['source_line']} actual={source_line_from_stderr(result.stderr)!r}"
                        )
                    if result.stderr:
                        print(f"  stderr={result.stderr.strip()!r}")

    print(
        "Ringkasan konformansi: "
        f"{states['PASS']} PASS, {states['FAIL']} FAIL, "
        f"{states['UNSUPPORTED']} UNSUPPORTED"
    )
    return 1 if states["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
