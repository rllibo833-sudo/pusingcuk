"""Bounded, auditable compiler/runtime diagnosis loop for PusingCuk.

It records reproducible diagnostics and proposes known-safe repair hints. It
never edits source, invokes a remote model, posts accounting entries, or merges
code automatically. A future local AI adapter can consume this stable report.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
REPAIR_CATALOG = {
 "SYNTAX": {"action":"Inspect the reported line and surrounding block terminators.","risk":"manual_review"},
 "RUNTIME": {"action":"Reproduce with the same input; inspect the first runtime diagnostic and add a regression fixture.","risk":"manual_review"},
 "OUTPUT_MISMATCH": {"action":"Do not rewrite expected output to hide the failure. Compare source semantics and interpreter output, then add a minimized fixture.","risk":"manual_review"},
 "TIMEOUT": {"action":"Reduce the input and check loops/recursion; keep the timeout bounded.","risk":"manual_review"},
 "UNKNOWN": {"action":"Preserve the complete diagnostic and request human review; no automatic patch is safe.","risk":"manual_review"},
}

def run_case(source: Path, expected: Sequence[str] | None = None, timeout: float = 5.0) -> dict:
    source = source.resolve()
    try:
        source.relative_to(ROOT)
    except ValueError:
        return {"status":"rejected","code":"SOURCE_OUTSIDE_REPOSITORY","source":str(source)}
    if source.suffix != ".cuk" or not source.is_file():
        return {"status":"rejected","code":"SOURCE_NOT_CUK","source":str(source)}
    raw=source.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    base={"source":str(source.relative_to(ROOT)),"source_sha256":digest,"timeout_seconds":timeout}
    try:
        check=subprocess.run([sys.executable,str(ROOT/"pusingcuk_new.py"),"--check",str(source)],
             cwd=ROOT,capture_output=True,text=True,timeout=timeout)
        if check.returncode:
            diagnostic=check.stderr.strip() or check.stdout.strip()
            kind="SYNTAX"
            return _report(base,kind,"compile_failed",check.returncode,diagnostic,None)
        execute=subprocess.run([sys.executable,str(ROOT/"pusingcuk_new.py"),str(source)],
             cwd=ROOT,capture_output=True,text=True,timeout=timeout)
        if execute.returncode:
            diagnostic=execute.stderr.strip() or execute.stdout.strip()
            return _report(base,"RUNTIME","runtime_failed",execute.returncode,diagnostic,None)
        actual=execute.stdout.splitlines()
        if expected is not None and actual != list(expected):
            return _report(base,"OUTPUT_MISMATCH","regression_failed",0,
                "Output berbeda dari fixture yang dikunci.",{"expected":list(expected),"actual":actual})
        return {**base,"status":"passed","code":"OK","exit_code":0,"stdout":actual,"diagnostic":None,"repair":None}
    except subprocess.TimeoutExpired as exc:
        diagnostic=(exc.stderr or b"").decode("utf-8","replace") if isinstance(exc.stderr,bytes) else (exc.stderr or "")
        return _report(base,"TIMEOUT","timed_out",None,diagnostic,None)

def _report(base: dict, kind: str, status: str, exit_code, diagnostic: str, output) -> dict:
    return {**base,"status":status,"code":kind,"exit_code":exit_code,
            "diagnostic":diagnostic[:12000],"output_comparison":output,
            "repair":{**REPAIR_CATALOG.get(kind,REPAIR_CATALOG["UNKNOWN"]),
                      "source_sha256":base["source_sha256"],"automatic_apply":False}}

def evaluate_fixtures(fixtures: list[dict]) -> dict:
    results=[]
    for fixture in fixtures:
        if set(fixture) - {"source","expected","id"}:
            results.append({"id":fixture.get("id","unknown"),"status":"rejected","code":"INVALID_FIXTURE_SCHEMA"})
            continue
        expected=fixture.get("expected")
        if expected is not None and (not isinstance(expected,list) or any(not isinstance(x,str) for x in expected)):
            results.append({"id":fixture.get("id","unknown"),"status":"rejected","code":"INVALID_EXPECTED_OUTPUT"})
            continue
        result=run_case(ROOT/str(fixture.get("source","")),expected)
        result["fixture_id"]=fixture.get("id","unnamed")
        results.append(result)
    return {"schema_version":"pusingcuk.diagnostic-report.v1","total":len(results),
            "passed":sum(r["status"]=="passed" for r in results),
            "failed":sum(r["status"]!="passed" for r in results),"results":results}

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("--expected",type=Path,help="UTF-8 expected stdout fixture, one line per output")
    p.add_argument("--json",action="store_true")
    a=p.parse_args()
    expected=a.expected.read_text(encoding="utf-8").splitlines() if a.expected else None
    result=run_case(a.source,expected)
    if a.json: print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print(f'{result["status"]}: {result["code"]} — {result["source"]}')
        if result.get("diagnostic"): print(result["diagnostic"])
        if result.get("repair"): print("Saran:",result["repair"]["action"],"(tidak diterapkan otomatis)")
    raise SystemExit(0 if result["status"]=="passed" else 1)
if __name__=="__main__": main()
