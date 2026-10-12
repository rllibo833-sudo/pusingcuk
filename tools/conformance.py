#!/usr/bin/env python3
"""Run the manifest-driven Pusingcuk cross-runtime conformance suite."""
from __future__ import annotations

import json
import os
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
ALLOWED_EXPECTED_KEYS = {"exit_code", "stdout", "stderr_class", "stdin"}
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
        if not source_path.is_file() or source_path.suffix != ".pusingcuk":
            raise ManifestError(f"{fixture_id}: source harus file .pusingcuk yang ada")

        expected = item.get("expected")
        if not isinstance(expected, dict) or set(expected) - ALLOWED_EXPECTED_KEYS:
            raise ManifestError(f"{fixture_id}: expected tidak valid")
        if not isinstance(expected.get("exit_code"), int) or isinstance(expected.get("exit_code"), bool):
            raise ManifestError(f"{fixture_id}: expected.exit_code harus integer")
        if not isinstance(expected.get("stdout"), str):
            raise ManifestError(f"{fixture_id}: expected.stdout harus teks")
        stderr_class = expected.get("stderr_class")
        if stderr_class not in (None, "error"):
            raise ManifestError(f"{fixture_id}: stderr_class hanya boleh null atau 'error'")
        if stderr_class is None and expected["exit_code"] != 0:
            raise ManifestError(f"{fixture_id}: kasus gagal wajib menetapkan stderr_class")
        if stderr_class == "error" and expected["exit_code"] == 0:
            raise ManifestError(f"{fixture_id}: kasus sukses tidak boleh mengharapkan error")
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
    if returncode != 0 and stderr.strip():
        return "error"
    return None


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
                matches = (
                    result.returncode == expected["exit_code"]
                    and result.stdout == expected["stdout"]
                    and actual_class == expected.get("stderr_class")
                )
                if matches:
                    states["PASS"] += 1
                    print(f"PASS {label}")
                else:
                    states["FAIL"] += 1
                    print(f"FAIL {label}")
                    print(f"  exit: expected={expected['exit_code']} actual={result.returncode}")
                    print(f"  stdout expected={expected['stdout']!r} actual={result.stdout!r}")
                    print(f"  stderr_class expected={expected.get('stderr_class')!r} actual={actual_class!r}")
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
