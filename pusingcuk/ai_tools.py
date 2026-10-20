"""Installed-package check for the AI conformance manifest."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
def main(argv=None):
    p=argparse.ArgumentParser(prog="python -m pusingcuk.ai_tools")
    p.add_argument("--check-fixture",action="store_true"); p.add_argument("--fixture-id")
    a=p.parse_args(argv)
    if not a.check_fixture: p.error("use --check-fixture")
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    path = bundle_root / "library" / "conformance_manifest.json"
    try:
        data=json.loads(path.read_text(encoding="utf-8")); fixtures=data["fixtures"]
        if not isinstance(fixtures,list) or not fixtures: raise ValueError("empty manifest")
        ids=[x["id"] for x in fixtures]
        if any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)): raise ValueError("invalid or duplicate fixture IDs")
        if a.fixture_id and a.fixture_id not in set(ids): raise ValueError("fixture ID not found: "+a.fixture_id)
    except (OSError,UnicodeError,json.JSONDecodeError,KeyError,TypeError,ValueError) as exc:
        print("CONFORMANCE_MANIFEST_INVALID: "+str(exc),file=sys.stderr); return 1
    print(f"CONFORMANCE_MANIFEST_OK fixtures={len(ids)} path={path}"); return 0
if __name__=="__main__": raise SystemExit(main())
