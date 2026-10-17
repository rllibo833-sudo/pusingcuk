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
    source_path=ROOT/base["source"]
    try:
        source_text=source_path.read_text(encoding="utf-8")[:24000]
    except (OSError,UnicodeError):
        source_text=""
    diagnostic=diagnostic[:12000]
    return {**base,"status":status,"code":kind,"exit_code":exit_code,
            "diagnostic":diagnostic,"output_comparison":output,
            "repair":{**REPAIR_CATALOG.get(kind,REPAIR_CATALOG["UNKNOWN"]),
                      "source_sha256":base["source_sha256"],"automatic_apply":False},
            "ai_handoff":{
                "contract":"pusingcuk.ai.repair.v1",
                "mode":"proposal_only",
                "instruction":"Propose the smallest correction to the .cuk source. Explain the semantic reason, preserve unrelated behavior, and add a regression case. Never alter expected output merely to hide a failure.",
                "source":source_text,
                "source_sha256":base["source_sha256"],
                "diagnostic_code":kind,
                "diagnostic":diagnostic,
                "output_comparison":output,
                "constraints":["Use only documented PusingCuk syntax.","Do not apply edits automatically.","Do not claim a fix until compiler, runtime, and regression fixtures pass.","Preserve exact financial arithmetic and explicit invalid-input behavior."]
            }}

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


def validate_frontend_contract(source: Path | None = None) -> dict:
    """Validate frontend metadata without pretending to render a UI."""
    source = (source or ROOT/"apps/accounting/cukaccount_frontend.cuk").resolve()
    try:
        source.relative_to(ROOT)
    except ValueError:
        return {"status":"rejected","code":"SOURCE_OUTSIDE_REPOSITORY","errors":["source outside repository"]}
    if source.suffix != ".cuk" or not source.is_file():
        return {"status":"rejected","code":"SOURCE_NOT_CUK","errors":["frontend source must be a .cuk file"]}
    directives=[line.strip()[2:].strip() for line in source.read_text(encoding="utf-8").splitlines()
                if line.strip().startswith("# @")]
    errors=[]
    for prefix in ("@app ","@theme ","@navigation "):
        if not any(line.startswith(prefix) for line in directives):
            errors.append("missing directive "+prefix.strip())
    nav_line=next((line[len("@navigation "):] for line in directives if line.startswith("@navigation ")), "")
    nav_ids=[item.split(":",1)[0].strip() for item in nav_line.split(",") if ":" in item]
    screens=[line[len("@screen "):].split(":",1)[0].strip() for line in directives if line.startswith("@screen ")]
    required_screens={"home","transactions","ledger","reports","periods"}
    for name in sorted(required_screens-set(screens)): errors.append("missing screen "+name)
    for name in sorted(set(nav_ids)-set(screens)): errors.append("navigation route has no screen "+name)
    for name in sorted(set(screens)-set(nav_ids)): errors.append("screen is not navigable "+name)
    for prefix,required in {
        "@field ":{"date","description","account","counter_account","debit","credit"},
        "@action ":{"validate","save_draft","post_journal"},
    }.items():
        names=[line[len(prefix):].split(":",1)[0].strip() for line in directives if line.startswith(prefix)]
        for name in sorted(required-set(names)): errors.append("missing "+prefix.strip()+" "+name)
        for name in sorted({n for n in names if names.count(n)>1}): errors.append("duplicate "+prefix.strip()+" "+name)
    return {"status":"passed" if not errors else "failed",
            "code":"FRONTEND_CONTRACT_OK" if not errors else "FRONTEND_CONTRACT_INVALID",
            "source":str(source.relative_to(ROOT)),"errors":errors,
            "navigation":nav_ids,"screens":screens}

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("--expected",type=Path,help="UTF-8 expected stdout fixture, one line per output")
    p.add_argument("--json",action="store_true")
    p.add_argument("--frontend-contract",action="store_true",help="Validate frontend metadata rather than execute the source")
    a=p.parse_args()
    if a.frontend_contract:
        result=validate_frontend_contract(a.source)
        if a.json: print(json.dumps(result,ensure_ascii=False,indent=2))
        else:
            print(f'{result["status"]}: {result["code"]} — {result.get("source", str(a.source))}')
            for error in result.get("errors", []): print(error)
        raise SystemExit(0 if result["status"]=="passed" else 1)
    expected=a.expected.read_text(encoding="utf-8").splitlines() if a.expected else None
    result=run_case(a.source,expected)
    if a.json: print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print(f'{result["status"]}: {result["code"]} — {result["source"]}')
        if result.get("diagnostic"): print(result["diagnostic"])
        if result.get("repair"): print("Saran:",result["repair"]["action"],"(tidak diterapkan otomatis)")
    raise SystemExit(0 if result["status"]=="passed" else 1)
if __name__=="__main__": main()
