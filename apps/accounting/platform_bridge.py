"""Capability-limited CukAccount platform bridge dispatcher.

Storage adapters are injected by the host. This module does not expose arbitrary
SQL, raw secure-store keys, or unrestricted filesystem access.
"""
from __future__ import annotations
from typing import Any, Callable

CONTRACT_VERSION = "cukaccount.platform.v1"
ALLOWED_OPERATIONS = {
    "db.query_accounts", "db.save_journal_draft", "db.post_journal",
    "db.get_general_ledger", "db.close_period", "backup.export",
    "backup.restore", "secure_store.get_key_metadata",
}

class BridgeError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

def validate_envelope(request: Any) -> dict:
    if not isinstance(request, dict):
        raise BridgeError("INVALID_REQUEST", "Request harus berupa objek.")
    if set(request) != {"contract_version", "request_id", "operation", "input"}:
        raise BridgeError("INVALID_REQUEST", "Field request tidak sesuai kontrak.")
    if request["contract_version"] != CONTRACT_VERSION:
        raise BridgeError("UNSUPPORTED_CONTRACT", "Versi bridge tidak didukung.")
    if not isinstance(request["request_id"], str) or not 1 <= len(request["request_id"]) <= 128:
        raise BridgeError("INVALID_REQUEST_ID", "request_id wajib berupa string 1-128 karakter.")
    if not isinstance(request["operation"], str) or request["operation"] not in ALLOWED_OPERATIONS:
        raise BridgeError("OPERATION_DENIED", "Operasi bridge tidak diizinkan.")
    if not isinstance(request["input"], dict):
        raise BridgeError("INVALID_INPUT", "Input operasi harus berupa objek.")
    return request

class PlatformBridge:
    """Dispatches only explicitly registered host capabilities."""
    def __init__(self, handlers: dict[str, Callable[[dict], Any]]):
        unknown = set(handlers) - ALLOWED_OPERATIONS
        if unknown:
            raise ValueError("Handler operasi tidak diizinkan: " + ", ".join(sorted(unknown)))
        self._handlers = dict(handlers)

    def dispatch(self, request: Any) -> dict:
        req = validate_envelope(request)
        handler = self._handlers.get(req["operation"])
        if handler is None:
            return {"contract_version": CONTRACT_VERSION, "request_id": req["request_id"],
                    "status": "denied", "diagnostic": {"code": "CAPABILITY_UNAVAILABLE"}}
        try:
            result = handler(req["input"])
        except BridgeError as exc:
            return {"contract_version": CONTRACT_VERSION, "request_id": req["request_id"],
                    "status": "rejected", "diagnostic": {"code": exc.code, "message": str(exc)}}
        return {"contract_version": CONTRACT_VERSION, "request_id": req["request_id"],
                "status": "succeeded", "result": result}
