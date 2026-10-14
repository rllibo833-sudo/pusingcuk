"""Small allowlisted tool registry for PusingCuk's local AI assistant."""
from __future__ import annotations

import json
import os
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener

from library.knowledge_grounding import rank_knowledge

_RUNNER_URL = "http://127.0.0.1:8787/v1/execute"
_THRESHOLD_SHA256 = "e79058b314d921a4b4353133b30a7a7b0da64d32785a39f66cb5ce356406067d"
_MAX_RULE_INPUT = 1_000_000_000_000


class ToolRegistry:
    """Expose only explicitly registered, schema-validated operations."""

    def __init__(self, documents: list[dict[str, Any]]):
        self.documents = documents
        self.by_id = {doc["id"]: doc for doc in documents}
        self.definitions = [
            {
                "type": "function",
                "function": {
                    "name": "knowledge_search",
                    "description": "Cari dokumen proyek yang terkurasi. Gunakan untuk memverifikasi klaim khusus PusingCuk, CORE, dan keputusan Founder.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "minLength": 1, "maxLength": 300},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 3},
                        },
                        "required": ["query"], "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "budget_threshold",
                    "description": "Jalankan aturan anggaran deterministik yang terdaftar dan terisolasi. Tidak menjalankan source dari model. Gunakan hanya bila pengguna memberi nominal dan batas anggaran.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nominal": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
                            "batas": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
                        },
                        "required": ["nominal", "batas"], "additionalProperties": False,
                    },
                },
            },
        ]

    def execute(self, name: str, arguments: Any) -> dict[str, Any]:
        if not isinstance(arguments, dict):
            return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
        if name == "knowledge_search":
            if set(arguments) - {"query", "limit"}:
                return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
            query = arguments.get("query")
            limit = arguments.get("limit", 3)
            if not isinstance(query, str) or not query.strip() or len(query) > 300:
                return {"ok": False, "error": "KNOWLEDGE_QUERY_INVALID"}
            if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 3:
                return {"ok": False, "error": "KNOWLEDGE_LIMIT_INVALID"}
            results = rank_knowledge(self.documents, query, limit=limit)
            return {"ok": True, "result_count": len(results), "results": results}
        if name == "budget_threshold":
            if set(arguments) != {"nominal", "batas"}:
                return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
            for key in ("nominal", "batas"):
                value = arguments[key]
                if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= _MAX_RULE_INPUT:
                    return {"ok": False, "error": "RULE_INPUT_INVALID"}
            return self._run_registered_threshold(arguments)
        return {"ok": False, "error": "TOOL_NOT_ALLOWLISTED"}

    @staticmethod
    def _run_registered_threshold(arguments: dict[str, int]) -> dict[str, Any]:
        token = os.environ.get("PUSINGCUK_RUNNER_TOKEN", "")
        if len(token) < 32:
            return {"ok": False, "error": "RULE_RUNNER_NOT_CONFIGURED"}
        parsed = urlparse(_RUNNER_URL)
        if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.path != "/v1/execute":
            return {"ok": False, "error": "RULE_RUNNER_ENDPOINT_INVALID"}
        body = {
            "contract_version": "pusingcuk.core.tool.v1",
            "request_id": str(uuid.uuid4()),
            "program_id": "budget.threshold.v1",
            "program_sha256": _THRESHOLD_SHA256,
            "language_version": "0.5-dev",
            "entrypoint": "status_anggaran",
            "capabilities": [],
            "limits": {"timeout_ms": 3000, "input_bytes": 128, "output_bytes": 1024},
            "input": arguments,
        }
        request = Request(
            _RUNNER_URL, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        )
        try:
            opener = build_opener(ProxyHandler({}))
            with opener.open(request, timeout=4) as response:
                raw = response.read(4097)
                if len(raw) > 4096:
                    return {"ok": False, "error": "RULE_RUNNER_RESPONSE_TOO_LARGE"}
                result = json.loads(raw.decode("utf-8"))
        except HTTPError as exc:
            return {"ok": False, "error": "RULE_RUNNER_HTTP_ERROR", "status": exc.code}
        except (URLError, TimeoutError, OSError):
            return {"ok": False, "error": "RULE_RUNNER_UNAVAILABLE"}
        except (UnicodeError, json.JSONDecodeError):
            return {"ok": False, "error": "RULE_RUNNER_RESPONSE_INVALID"}
        if not isinstance(result, dict) or result.get("status") != "succeeded" or result.get("program_id") != "budget.threshold.v1":
            return {"ok": False, "error": "RULE_EXECUTION_FAILED"}
        if result.get("program_sha256") != _THRESHOLD_SHA256 or result.get("result") not in {
            "DALAM_BATAS", "PERLU_PERSETUJUAN", "INPUT_TIDAK_VALID",
        }:
            return {"ok": False, "error": "RULE_EVIDENCE_INVALID"}
        return {
            "ok": True, "program_id": result["program_id"], "result": result["result"],
            "source_commit": result.get("source_commit"), "runtime_build_sha": result.get("runtime_build_sha"),
            "elapsed_ms": result.get("elapsed_ms"),
        }
