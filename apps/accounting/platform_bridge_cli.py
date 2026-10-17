"""One-request JSON entry point for the Electron host. No arbitrary SQL or paths."""
import json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from apps.accounting.platform_bridge import create_sqlite_bridge

def main():
    raw=sys.stdin.read(65537)
    if len(raw)>65536:
        print(json.dumps({"status":"rejected","diagnostic":{"code":"REQUEST_TOO_LARGE"}})); return 2
    try: request=json.loads(raw)
    except (ValueError,TypeError):
        print(json.dumps({"status":"rejected","diagnostic":{"code":"INVALID_JSON"}})); return 2
    db_path=os.environ.get("CUKACCOUNT_DB")
    if not db_path:
        print(json.dumps({"status":"rejected","diagnostic":{"code":"DATABASE_PATH_UNAVAILABLE"}})); return 2
    bridge,store=create_sqlite_bridge(Path(db_path))
    try: response=bridge.dispatch(request)
    except Exception as exc:
        response={"status":"rejected","diagnostic":{"code":getattr(exc,"code","INVALID_REQUEST"),"message":str(exc)[:240]}}
    finally: store.close()
    print(json.dumps(response,ensure_ascii=False,separators=(",",":")))
    return 0 if response.get("status")=="succeeded" else 1
if __name__=="__main__": raise SystemExit(main())
