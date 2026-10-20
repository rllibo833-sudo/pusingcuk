#!/usr/bin/env python3
"""V6 compatibility entry point: dry-run, review-only language-evolution proposal."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from tools.evolve_daemon import inspect_proposal
ROOT=Path(__file__).resolve().parent
FALLBACK=("jedor","gebber","bacrit","nyalak","muncrat","semprot","senggol","berak","crot","koar2")
def main(argv=None):
    p=argparse.ArgumentParser(description="V6 dry-run proposal; no file writes or Git push.")
    p.add_argument("--canonical",default="hedeh"); p.add_argument("--alias")
    a=p.parse_args(argv)
    if a.alias: alias=a.alias
    else:
        try:
            data=json.loads((ROOT/"library"/"kosakata.json").read_text(encoding="utf-8"))
            entries={x.get("word"):set(x.get("aliases",[])) for x in data.get("keywords",[]) if isinstance(x,dict)}
            used=entries.get(a.canonical,set())
        except (OSError,json.JSONDecodeError) as exc:
            print(json.dumps({"status":"rejected","reason":str(exc)})); return 1
        alias=next((x for x in FALLBACK if x!=a.canonical and x not in used),"v6_candidate")
    result=inspect_proposal(a.canonical,alias)
    result.update({"mode":"DRY-RUN","writes_files":False,"git_side_effects":False})
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result.get("status")=="review_required" else 1
if __name__=="__main__": raise SystemExit(main())
