#!/usr/bin/env python3
"""Run every conformance fixture against each available PusingCuk target.

Writes raw per-target logs and a machine-readable summary. Unsupported backends are
reported explicitly; compilation failures are never silently treated as unsupported.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.conformance import load_manifest, build_native, classify_stderr, source_line_from_stderr

OUT = Path(os.environ.get("PUSINGCUK_MATRIX_OUT", "artifacts/fixture-matrix"))
OUT.mkdir(parents=True, exist_ok=True)
TIMEOUT = 8
TARGETS = ("reference", "native", "javascript", "python_transpiler", "html", "vm")


def execute(command, stdin_text=""):
    try:
        p = subprocess.run(command, cwd=ROOT, input=stdin_text, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=TIMEOUT, check=False)
        return p.returncode, p.stdout, p.stderr, None
    except subprocess.TimeoutExpired as exc:
        return None, exc.stdout or "", exc.stderr or "", "timeout"
    except (OSError, ValueError) as exc:
        return None, "", str(exc), "harness_error"


def main():
    fixtures = load_manifest()
    rows = []
    raw_lines = []
    with tempfile.TemporaryDirectory(prefix="pusingcuk-matrix-") as tmp:
        tmp = Path(tmp)
        native_path = tmp / "pusingcuk-native"
        native_ready, native_error = build_native(native_path)
        node = shutil.which("node")
        for item, source_path in fixtures:
            expected = item["expected"]
            stdin_text = expected.get("stdin", "")
            per_fixture = {"id": item["id"], "source": item["source"], "targets": {}}
            for target in TARGETS:
                declared = item.get("runtimes", {})
                if target == "reference" and declared.get("reference") == "unsupported":
                    status, reason = "unsupported", "manifest declares unsupported"
                    observation = {}
                elif target == "native" and declared.get("native") == "unsupported":
                    status, reason, observation = "unsupported", "manifest declares unsupported", {}
                elif target == "html":
                    status, reason, observation = "unsupported", "HTML executable backend not present in repository", {}
                elif target == "javascript" and not node:
                    status, reason, observation = "unsupported", "Node.js is not installed on runner", {}
                elif target == "native" and not native_ready:
                    status, reason, observation = "unavailable", native_error or "native build failed", {}
                else:
                    generated = tmp / (target + "-" + str(len(rows)) + "-" + item["id"].replace(".", "_"))
                    if target == "reference":
                        command = [sys.executable, str(ROOT / "pusingcuk_new.py"), str(source_path)]
                    elif target == "native":
                        command = [str(native_path), str(source_path)]
                    elif target == "javascript":
                        generated = generated.with_suffix(".js")
                        compile_cmd = [sys.executable, "-m", "compiler.js_backend", str(source_path), "-o", str(generated)]
                        cr, co, ce, err = execute(compile_cmd)
                        if err or cr != 0:
                            status, reason, observation = "failed", "JavaScript compile failed" + (": " + ce.strip() if ce.strip() else ""), {"compile_stdout": co, "compile_stderr": ce, "compile_exit_code": cr}
                            per_fixture["targets"][target] = {"status": status, "reason": reason, **observation}
                            raw_lines.append(f"[{item['id']}][{target}] {status}: {reason}\n{ce}")
                            continue
                        command = [node, str(generated)]
                    elif target == "python_transpiler":
                        generated = generated.with_suffix(".py")
                        command_compile = [sys.executable, "-m", "compiler.python_backend", str(source_path), "-o", str(generated)]
                        cr, co, ce, err = execute(command_compile)
                        if err or cr != 0:
                            status, reason, observation = "failed", "Python transpiler compile failed" + (": " + ce.strip() if ce.strip() else ""), {"compile_stdout": co, "compile_stderr": ce, "compile_exit_code": cr}
                            per_fixture["targets"][target] = {"status": status, "reason": reason, **observation}
                            raw_lines.append(f"[{item['id']}][{target}] {status}: {reason}\n{ce}")
                            continue
                        command = [sys.executable, str(generated)]
                    elif target == "vm":
                        generated = generated.with_suffix(".json")
                        inline = ("import json,sys; from pathlib import Path; "
                                  "from compiler.bytecode import compile_source; "
                                  "p=Path(sys.argv[1]); "
                                  "Path(sys.argv[2]).write_text(json.dumps(compile_source(p.read_text(encoding='utf-8'), p.name)), encoding='utf-8')")
                        cr, co, ce, err = execute([sys.executable, "-c", inline, str(source_path), str(generated)])
                        if err or cr != 0:
                            status, reason, observation = "failed", "VM bytecode compile failed" + (": " + ce.strip() if ce.strip() else ""), {"compile_stdout": co, "compile_stderr": ce, "compile_exit_code": cr}
                            per_fixture["targets"][target] = {"status": status, "reason": reason, **observation}
                            raw_lines.append(f"[{item['id']}][{target}] {status}: {reason}\n{ce}")
                            continue
                        command = [sys.executable, "-m", "compiler.vm", str(generated)]
                    rc, stdout, stderr, run_error = execute(command, stdin_text)
                    actual_class = classify_stderr(rc if rc is not None else 1, stderr)
                    actual_line = source_line_from_stderr(stderr)
                    matched = (run_error is None and rc == expected.get("exit_code", 0)
                               and stdout == expected.get("stdout", "")
                               and actual_class == expected.get("stderr_class")
                               and (expected.get("source_line") is None or actual_line == expected["source_line"]))
                    status = "passed" if matched else ("timeout" if run_error == "timeout" else "failed")
                    reason = "" if matched else (run_error or "expected/observed mismatch")
                    observation = {"exit_code": rc, "stdout": stdout, "stderr": stderr,
                                   "stderr_class": actual_class, "source_line": actual_line,
                                   "matched": matched}
                per_fixture["targets"][target] = {"status": status, **({"reason": reason} if reason else {}), **observation}
                raw_lines.append(f"[{item['id']}][{target}] {status}\n{json.dumps(per_fixture['targets'][target], ensure_ascii=False)}")
            rows.append(per_fixture)
    summary = {"schema_version": 1, "fixture_count": len(fixtures), "targets": {}, "python_free_score": None,
               "python_free_method": "Native C only: passed native fixtures divided by fixtures whose manifest marks native required or optional; unsupported excluded. VM excluded because it imports evaluator Python helpers."}
    for target in TARGETS:
        results = [row["targets"][target]["status"] for row in rows]
        summary["targets"][target] = {state: results.count(state) for state in ("passed", "failed", "timeout", "unsupported", "unavailable")}
    eligible = [row for row in rows if next((item.get("runtimes", {}).get("native") for item, _ in fixtures if item["id"] == row["id"]), None) in {"required", "optional"}]
    passed_native = sum(row["targets"]["native"]["status"] == "passed" for row in eligible)
    summary["python_free_score"] = {"numerator": passed_native, "denominator": len(eligible),
                                    "percent": round(100 * passed_native / len(eligible), 2) if eligible else None,
                                    "runtime": "native C", "excludes_unsupported": True}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "raw.log").write_text("\n\n".join(raw_lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if any(v["failed"] or v["timeout"] or v["unavailable"] for k, v in summary["targets"].items() if k in {"reference", "native"}) else 0


if __name__ == "__main__":
    raise SystemExit(main())
