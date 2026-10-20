#!/usr/bin/env python3
"""Deprecated compatibility wrapper; never edits vocabulary, parser, or app files."""
from __future__ import annotations
import argparse,json
from tools.evolve_daemon import inspect_proposal
def main(argv=None):
    p=argparse.ArgumentParser(description="fix_parser_all: review-only; no files are modified.")
    p.add_argument("--canonical",default="hedeh"); p.add_argument("--alias",required=True)
    a=p.parse_args(argv); result=inspect_proposal(a.canonical,a.alias)
    result.update({"mode":"REVIEW-ONLY","writes_files":False,"git_side_effects":False})
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result.get("status")=="review_required" else 1
if __name__=="__main__": raise SystemExit(main())
