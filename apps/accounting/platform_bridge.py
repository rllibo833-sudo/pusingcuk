"""Typed, capability-limited bridge between UI events and accounting storage."""
from __future__ import annotations
from typing import Any, Callable
import importlib.util
from pathlib import Path

CONTRACT_VERSION = "cukaccount.platform.v1"
ALLOWED_OPERATIONS = {
    "db.query_accounts", "db.save_journal_draft", "db.post_journal",
    "db.get_general_ledger", "db.close_period", "backup.export",
    "backup.restore", "secure_store.get_key_metadata",
}
INPUT_FIELDS = {
 "db.query_accounts": set(),
 "db.save_journal_draft": {"entry_id","date","description","lines","idempotency_key"},
 "db.post_journal": {"entry_id","idempotency_key"},
 "db.get_general_ledger": {"account_id","start_date","end_date"},
 "db.close_period": {"period_id","reason"},
 "backup.export": {"destination_token"},
 "backup.restore": {"source_token","confirmation"},
 "secure_store.get_key_metadata": set(),
}
REQUIRED_FIELDS = {
 "db.query_accounts": set(),
 "db.save_journal_draft": {"date","description","lines"},
 "db.post_journal": {"entry_id","idempotency_key"},
 "db.get_general_ledger": {"account_id"},
 "db.close_period": {"period_id","reason"},
 "backup.export": {"destination_token"},
 "backup.restore": {"source_token","confirmation"},
 "secure_store.get_key_metadata": set(),
}
class BridgeError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message); self.code=code

def validate_envelope(request: Any) -> dict:
    if not isinstance(request,dict): raise BridgeError("INVALID_REQUEST","Request harus berupa objek.")
    if set(request)!={"contract_version","request_id","operation","input"}: raise BridgeError("INVALID_REQUEST","Field request tidak sesuai kontrak.")
    if request["contract_version"]!=CONTRACT_VERSION: raise BridgeError("UNSUPPORTED_CONTRACT","Versi bridge tidak didukung.")
    if not isinstance(request["request_id"],str) or not 1<=len(request["request_id"])<=128: raise BridgeError("INVALID_REQUEST_ID","request_id wajib berupa string 1-128 karakter.")
    op=request["operation"]
    if not isinstance(op,str) or op not in ALLOWED_OPERATIONS: raise BridgeError("OPERATION_DENIED","Operasi bridge tidak diizinkan.")
    payload=request["input"]
    if not isinstance(payload,dict): raise BridgeError("INVALID_INPUT","Input operasi harus berupa objek.")
    extra=set(payload)-INPUT_FIELDS[op]; missing=REQUIRED_FIELDS[op]-set(payload)
    if extra: raise BridgeError("INVALID_INPUT_FIELDS","Field input tidak diizinkan: "+", ".join(sorted(extra)))
    if missing: raise BridgeError("MISSING_INPUT_FIELDS","Field wajib belum ada: "+", ".join(sorted(missing)))
    return request

class PlatformBridge:
    def __init__(self,handlers:dict[str,Callable[[dict],Any]]):
        unknown=set(handlers)-ALLOWED_OPERATIONS
        if unknown: raise ValueError("Handler operasi tidak diizinkan: "+", ".join(sorted(unknown)))
        self._handlers=dict(handlers)
    def dispatch(self,request:Any)->dict:
        req=validate_envelope(request); op=req["operation"]; handler=self._handlers.get(op)
        if handler is None:
            return {"contract_version":CONTRACT_VERSION,"request_id":req["request_id"],"status":"denied","diagnostic":{"code":"CAPABILITY_UNAVAILABLE"}}
        try: result=handler(req["input"])
        except BridgeError as exc:
            return {"contract_version":CONTRACT_VERSION,"request_id":req["request_id"],"status":"rejected","diagnostic":{"code":exc.code,"message":str(exc)}}
        except Exception as exc:
            # Do not leak SQL, paths, or internal exceptions to the UI.
            code=getattr(exc,"code","STORAGE_REJECTED")
            return {"contract_version":CONTRACT_VERSION,"request_id":req["request_id"],"status":"rejected","diagnostic":{"code":code,"message":str(exc)[:240]}}
        return {"contract_version":CONTRACT_VERSION,"request_id":req["request_id"],"status":"succeeded","result":result}

def create_sqlite_bridge(database: str | Path) -> tuple[PlatformBridge, Any]:
    """Construct a bridge backed by the local SQLite reference adapter."""
    module_path=Path(__file__).with_name("sqlite_store.py")
    spec=importlib.util.spec_from_file_location("cukaccount_sqlite_store",module_path)
    if spec is None or spec.loader is None: raise RuntimeError("SQLite adapter tidak tersedia.")
    module=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name]=module; spec.loader.exec_module(module)
    store=module.CukAccountSQLite(database)
    def call(method):
        def handler(payload):
            try: return getattr(store,method)(payload)
            except module.StorageError as exc: raise BridgeError(exc.code,str(exc)) from exc
        return handler
    handlers={
      "db.query_accounts":call("query_accounts"),
      "db.save_journal_draft":call("save_journal_draft"),
      "db.post_journal":call("post_journal"),
      "db.get_general_ledger":call("get_general_ledger"),
      "db.close_period":call("close_period"),
    }
    return PlatformBridge(handlers),store
