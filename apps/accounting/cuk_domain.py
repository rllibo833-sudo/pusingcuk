"""Invoke deterministic CukAccount domain functions through the PusingCuk interpreter."""
from __future__ import annotations
import subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BACKEND=ROOT/"apps/accounting/cukaccount_backend.cuk"

def _invoke(function: str, args: list[str], timeout: float=3.0) -> str:
    source=BACKEND.read_text(encoding="utf-8")
    # Keep only source declarations, never the smoke-test calls at the end.
    prefix=source.split("\nhedeh ",1)[0]
    program=prefix+"\nhedeh "+function+"("+", ".join(args)+")\nselesai jancuk\n"
    with tempfile.TemporaryDirectory(prefix="cuk-domain-") as directory:
        path=Path(directory)/"domain_call.cuk"; path.write_text(program,encoding="utf-8")
        checked=subprocess.run([sys.executable,str(ROOT/"pusingcuk_new.py"),"--check",str(path)],
            cwd=ROOT,capture_output=True,text=True,timeout=timeout)
        if checked.returncode: raise RuntimeError("DOMAIN_COMPILE_FAILED: "+(checked.stderr or checked.stdout)[:500])
        result=subprocess.run([sys.executable,str(ROOT/"pusingcuk_new.py"),str(path)],
            cwd=ROOT,capture_output=True,text=True,timeout=timeout)
        if result.returncode: raise RuntimeError("DOMAIN_RUNTIME_FAILED: "+(result.stderr or result.stdout)[:500])
        lines=result.stdout.splitlines()
        if len(lines)!=1: raise RuntimeError("DOMAIN_OUTPUT_INVALID")
        return lines[0]

def validate_journal(total_debit: int,total_credit: int,line_count: int,period_open: bool) -> str:
    for value in (total_debit,total_credit,line_count):
        if isinstance(value,bool) or not isinstance(value,int): raise ValueError("Domain input must be integer")
    if not isinstance(period_open,bool): raise ValueError("period_open must be bool")
    return _invoke("validasi_jurnal",[str(total_debit),str(total_credit),str(line_count),"benar" if period_open else "salah"])
