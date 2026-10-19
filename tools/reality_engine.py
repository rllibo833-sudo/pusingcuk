#!/usr/bin/env python3
"""Cuk Reality Engine: reproducible evidence for declared PusingCuk runtimes.

Only the checked-in conformance manifest is executed. This is not a sandbox.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.conformance import (  # noqa: E402
    build_native, classify_stderr, load_manifest, source_line_from_stderr,
)

REPORTS = ROOT / "reports"
MATRIX = REPORTS / "matrix.json"
HISTORY = REPORTS / "history.json"
COMPAT = ROOT / "docs" / "COMPATIBILITY.md"
README = ROOT / "README.md"
TIMEOUT = 5


def _run(command, stdin_text=""):
    try:
        p = subprocess.run(
            command, cwd=ROOT, input=stdin_text, text=True, encoding="utf-8",
            errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=TIMEOUT, check=False,
        )
        return p.returncode, p.stdout, p.stderr, None
    except subprocess.TimeoutExpired:
        return None, "", "", "timeout"
    except OSError as exc:
        return None, "", str(exc), "unavailable"


def _observe(command, stdin_text, expected):
    code, stdout, stderr, error = _run(command, stdin_text)
    if error:
        return {"status": error.upper(), "matched": False, "error": error}
    category = classify_stderr(code, stderr)
    line = source_line_from_stderr(stderr)
    matched = (
        code == expected["exit_code"]
        and stdout == expected["stdout"]
        and category == expected.get("stderr_class")
        and (expected.get("source_line") is None or line == expected["source_line"])
    )
    return {
        "status": "PASS" if matched else "FAIL",
        "matched": matched,
        "exit_code": code,
        "stdout": stdout,
        "stderr_class": category,
        "source_line": line,
        "stderr": stderr[:2000],
    }


def build_matrix():
    fixtures = load_manifest()
    REPORTS.mkdir(parents=True, exist_ok=True)
    rows = []
    counts = {"reference": {"pass": 0, "fail": 0, "unsupported": 0},
              "native": {"pass": 0, "fail": 0, "unsupported": 0}}
    native_needed = any(x["runtimes"].get("native") in {"required", "optional"} for x, _ in fixtures)
    with tempfile.TemporaryDirectory(prefix="cuk-reality-") as tmp:
        native = Path(tmp) / "pusingcuk-native"
        native_ok, native_error = build_native(native) if native_needed else (False, "")
        for item, source in fixtures:
            runtime_results = {}
            for runtime, state in sorted(item["runtimes"].items()):
                if state == "unsupported":
                    result = {"status": "UNSUPPORTED", "matched": False}
                    counts[runtime]["unsupported"] += 1
                elif runtime == "native" and not native_ok:
                    result = {"status": "UNAVAILABLE", "matched": False, "error": native_error}
                    counts[runtime]["fail"] += 1
                else:
                    command = (
                        [sys.executable, str(ROOT / "pusingcuk_new.py"), str(source)]
                        if runtime == "reference" else [str(native), str(source)]
                    )
                    result = _observe(command, item["expected"].get("stdin", ""), item["expected"])
                    counts[runtime]["pass" if result["matched"] else "fail"] += 1
                runtime_results[runtime] = result
            required = [name for name, state in item["runtimes"].items() if state == "required"]
            rows.append({
                "id": item["id"], "source": item["source"],
                "profile": item.get("profile", "unspecified"),
                "requires": item.get("requires", []),
                "expected": item["expected"], "runtimes": item["runtimes"],
                "results": runtime_results,
                "status": "PASS" if all(runtime_results.get(name, {}).get("matched") for name in required) else "FAIL",
            })
    native_required = sum(1 for item, _ in fixtures if item["runtimes"].get("native") == "required")
    native_pass = sum(1 for row in rows if row["runtimes"].get("native") == "required" and row["results"].get("native", {}).get("matched"))
    data = {
        "schema_version": 1,
        "engine": "Cuk Reality Engine",
        "manifest": "tests/conformance/manifest.json",
        "fixture_count": len(rows),
        "targets": ["reference", "native"],
        "counts": counts,
        "python_free_score": {
            "target": "native C runtime after compilation",
            "passed_required_fixtures": native_pass,
            "total_required_fixtures": native_required,
            "percent": round(100 * native_pass / native_required, 2) if native_required else 0,
            "note": "Does not mean compiler, build, tooling, or CI is Python-free.",
        },
        "fixtures": rows,
    }
    return data


def _render_compat(matrix):
    score = matrix["python_free_score"]
    lines = [
        "# PusingCuk Compatibility Evidence", "",
        "> Generated by `pusingcuk reality run`. Results describe the checked-in fixture manifest and this execution only.", "",
        f"- Fixtures: **{matrix['fixture_count']}**",
        f"- Reference: **{matrix['counts']['reference']['pass']} PASS**, {matrix['counts']['reference']['fail']} FAIL",
        f"- Native C: **{matrix['counts']['native']['pass']} PASS**, {matrix['counts']['native']['fail']} FAIL, {matrix['counts']['native']['unsupported']} UNSUPPORTED",
        f"- Python-Free Score (native required fixtures): **{score['percent']:.2f}%** ({score['passed_required_fixtures']}/{score['total_required_fixtures']})",
        "", "## Fixture evidence", "",
        "| Fixture | Reference | Native C | Overall |",
        "|---|---:|---:|---:|",
    ]
    for row in matrix["fixtures"]:
        ref = row["results"].get("reference", {}).get("status", "N/A")
        native = row["results"].get("native", {}).get("status", "N/A")
        lines.append(f"| `{row['id']}` | {ref} | {native} | {row['status']} |")
    lines += ["", "This report does not claim parity for targets absent from the manifest. A passing negative fixture means the expected diagnostic was observed.", ""]
    return "\n".join(lines)


def _render_svg(matrix):
    score = matrix["python_free_score"]
    label = f"Python-free native C {score['percent']:.2f}%"
    # Static SVG keeps badges offline and deterministic.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="270" height="20" role="img" aria-label="{label}">
<rect width="270" height="20" rx="3" fill="#555"/>
<rect x="155" width="115" height="20" rx="3" fill="#176b42"/>
<g fill="#fff" font-family="Verdana,sans-serif" font-size="11" text-anchor="middle">
<text x="77" y="14">Python-free native C</text><text x="212" y="14">{score["percent"]:.2f}%</text>
</g></svg>
'''


def render_outputs(matrix):
    return {
        MATRIX: json.dumps(matrix, ensure_ascii=False, indent=2) + "\n",
        COMPAT: _render_compat(matrix),
        ROOT / "docs" / "assets" / "python-free-score.svg": _render_svg(matrix),
    }


def run_report(check=False):
    try:
        matrix = build_matrix()
    except Exception as exc:
        print(f"reality: manifest/runtime gagal: {exc}", file=sys.stderr)
        return 2
    outputs = render_outputs(matrix)
    stale = []
    for path, content in outputs.items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    score = matrix["python_free_score"]
    print(f"Reality Engine: {matrix['fixture_count']} fixtures; Python-Free {score['passed_required_fixtures']}/{score['total_required_fixtures']} ({score['percent']:.2f}%).")
    print(f"Reference PASS/FAIL: {matrix['counts']['reference']['pass']}/{matrix['counts']['reference']['fail']}; native PASS/FAIL/UNSUPPORTED: {matrix['counts']['native']['pass']}/{matrix['counts']['native']['fail']}/{matrix['counts']['native']['unsupported']}.")
    if stale:
        print("Generated output stale: " + ", ".join(stale), file=sys.stderr)
        return 1
    if not check:
        print("Generated: reports/matrix.json, docs/COMPATIBILITY.md, docs/assets/python-free-score.svg")
    return 0


def diff_file(path_text):
    source = Path(path_text).expanduser().resolve()
    try:
        source.relative_to(ROOT)
    except ValueError:
        # Explicit user-provided source may live outside the repository.
        pass
    if not source.is_file() or source.suffix not in {".cuk", ".pusingcuk"}:
        print("reality diff: masukkan file .cuk/.pusingcuk yang ada.", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="cuk-reality-diff-") as tmp:
        native = Path(tmp) / "pusingcuk-native"
        ok, error = build_native(native)
        if not ok:
            print(f"native target unavailable: {error}", file=sys.stderr)
            return 2
        observations = {}
        for name, command in (
            ("reference", [sys.executable, str(ROOT / "pusingcuk_new.py"), str(source)]),
            ("native", [str(native), str(source)]),
        ):
            code, stdout, stderr, run_error = _run(command)
            observations[name] = {
                "status": "UNAVAILABLE" if run_error else "OK",
                "exit_code": code, "stdout": stdout,
                "stderr_class": classify_stderr(code, stderr) if not run_error else None,
                "source_line": source_line_from_stderr(stderr) if not run_error else None,
                "stderr": stderr[:2000], "error": run_error,
            }
    def normalized(item):
        return (item["status"], item["exit_code"], item["stdout"], item["stderr_class"], item["source_line"])
    mismatch = normalized(observations["reference"]) != normalized(observations["native"])
    print(json.dumps({"source": str(source), "mismatch": mismatch, "targets": observations}, ensure_ascii=False, indent=2))
    if mismatch:
        REPORTS.mkdir(parents=True, exist_ok=True)
        draft = [
            "## Bug parity: target outputs differ", "",
            f"Source: `{source.name}`", "",
            "### Reproducer", "", "Copy the complete source below to reproduce the mismatch.", "",
            "```cuk", source.read_text(encoding="utf-8").rstrip(), "```", "",
            "### Observed", "", "```json",
            json.dumps(observations, ensure_ascii=False, indent=2), "```", "",
            "### Expected", "",
            "Reference and native C should agree on exit code, stdout, diagnostic class, and source line.",
            "", "Label: `bug-parity`", "",
            "> This draft is a reproducible source snapshot, not an automatic token-level minimizer. Review before filing.",
        ]
        out = REPORTS / "issue-draft-bug-parity.md"
        out.write_text("\n".join(draft) + "\n", encoding="utf-8")
        print(f"Mismatch detected; issue draft written to {out.relative_to(ROOT)}.", file=sys.stderr)
        return 1
    print("No normalized mismatch found for the two available targets.")
    return 0


def report():
    if not MATRIX.is_file():
        print("Matrix belum ada. Jalankan: pusingcuk reality run", file=sys.stderr)
        return 2
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    score = matrix["python_free_score"]
    print(f"Fixtures: {matrix['fixture_count']}")
    print(f"Reference: {matrix['counts']['reference']}")
    print(f"Native: {matrix['counts']['native']}")
    print(f"Python-Free Score: {score['percent']:.2f}% ({score['passed_required_fixtures']}/{score['total_required_fixtures']})")
    if HISTORY.is_file():
        history = json.loads(HISTORY.read_text(encoding="utf-8"))
        print(f"Recorded history points: {len(history.get('records', []))}")
    else:
        print("History: no snapshots recorded yet.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pusingcuk reality", description="Evidence and parity tools for .cuk targets.")
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run", help="run fixture manifest and regenerate compatibility evidence")
    run_p.add_argument("--check", action="store_true", help="fail if generated files are stale")
    diff_p = sub.add_parser("diff", help="compare reference Python and native C on one source file")
    diff_p.add_argument("file")
    sub.add_parser("report", help="show latest matrix and Python-free score")
    args = parser.parse_args(argv)
    if args.command == "run":
        return run_report(check=args.check)
    if args.command == "diff":
        return diff_file(args.file)
    return report()


if __name__ == "__main__":
    raise SystemExit(main())
