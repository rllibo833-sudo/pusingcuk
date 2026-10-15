"""Offline end-to-end coverage for the local HTTP -> assistant -> .cuk rule path."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from library.ai_service import create_server
from library.assistant import PusingCukAssistant
from compiler.ir import from_source
from compiler.js_backend import generate
from library.ai_tools import _REGISTERED_RULES, _load_rule_source
from library.knowledge_grounding import load_index

_TOKEN = "offline-e2e-service-token-" + ("x" * 40)
_SESSION_ID = "e2e_session_0123456789"
_NODE = shutil.which("node")


class OfflineToolProvider:
    """Deterministic model double: it never opens a network connection."""

    def __init__(self, tool_name: str, arguments: dict):
        self.tool_name = tool_name
        self.arguments = arguments
        self.calls: list[dict] = []
        self.tool_results: list[dict] = []

    def generate_turn(self, messages, *, system_prompt=None, tools=None):
        self.calls.append({
            "messages": copy.deepcopy(messages),
            "system_prompt": system_prompt,
            "tools": copy.deepcopy(tools),
        })
        if len(self.calls) == 1:
            return {
                "content": "",
                "tool_calls": [{
                    "id": "offline-e2e-call-1",
                    "name": self.tool_name,
                    "arguments": self.arguments,
                }],
            }

        tool_messages = [item for item in messages if item.get("role") == "tool"]
        if not tool_messages:
            raise AssertionError("assistant must execute a tool before asking for the final turn")
        result = json.loads(tool_messages[-1]["content"])
        self.tool_results.append(result)

        if result.get("ok") is True and result.get("result") == "PERLU_PERSETUJUAN":
            answer = "Anggaran melebihi batas; aturan .cuk menghasilkan PERLU_PERSETUJUAN."
        elif result.get("error") == "TOOL_NOT_ALLOWLISTED":
            answer = "Permintaan alat ditolak karena alat itu tidak terdaftar dan tidak dijalankan."
        else:
            answer = "Hasil alat tidak dapat diverifikasi; tindakan lanjutan tidak dilakukan."
        return {"content": answer, "tool_calls": []}


class AIAssistantEndToEndTests(unittest.TestCase):
    """Exercise the real local HTTP server and .cuk runtime without model/network access."""

    def setUp(self):
        index_path = Path(__file__).resolve().parents[1] / "library" / "knowledge_index.json"
        self.documents = load_index(index_path)
        self.tool_name = "budget_threshold"
        self.tool_arguments = {"nominal": 120, "batas": 100}
        self.providers: list[OfflineToolProvider] = []
        self.assistants: list[PusingCukAssistant] = []

        self.server = create_server(
            "127.0.0.1",
            0,
            token=_TOKEN,
            assistant_factory=self._create_assistant,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def _create_assistant(self):
        provider = OfflineToolProvider(self.tool_name, dict(self.tool_arguments))
        assistant = PusingCukAssistant(provider, self.documents)
        self.providers.append(provider)
        self.assistants.append(assistant)
        return assistant

    def _post_chat(self, query: str):
        payload = json.dumps(
            {"session_id": _SESSION_ID, "query": query},
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            self.base_url + "/v1/chat",
            data=payload,
            headers={
                "Authorization": f"Bearer {_TOKEN}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_natural_language_http_request_executes_registered_cuk_rule(self):
        query = "Tolong cek apakah anggaran Rp120 melewati batas Rp100."
        status, payload = self._post_chat(query)

        self.assertEqual(status, 200, payload)
        self.assertEqual(payload["session_id"], _SESSION_ID)
        self.assertIn("PERLU_PERSETUJUAN", payload["answer"])
        self.assertEqual(len(self.assistants), 1)

        provider = self.providers[0]
        self.assertEqual(len(provider.calls), 2, "expected model-tool-model orchestration")
        self.assertEqual(provider.calls[0]["messages"][-1], {"role": "user", "content": query})
        offered = {
            item["function"]["name"]: item["function"]
            for item in provider.calls[0]["tools"]
        }
        self.assertIn("budget_threshold", offered)
        budget_schema = offered["budget_threshold"]["parameters"]
        self.assertEqual(budget_schema["required"], ["nominal", "batas"])
        self.assertIs(budget_schema["additionalProperties"], False)

        self.assertEqual(len(provider.tool_results), 1)
        result = provider.tool_results[0]
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["program_id"], "budget.threshold.v1")
        self.assertEqual(result["result"], "PERLU_PERSETUJUAN")
        self.assertEqual(result["capabilities"], [])
        # This explicitly documents the current trust boundary: hash-pinned rule,
        # but not an operating-system sandbox.
        self.assertEqual(
            result["execution_boundary"],
            "fixed-hash-local-rule-not-os-sandbox",
        )

    @unittest.skipUnless(_NODE, "Node.js diperlukan untuk menjalankan artefak build JavaScript")
    def test_http_ai_tool_and_built_artifact_agree_end_to_end(self):
        query = "Tolong cek apakah anggaran Rp120 melewati batas Rp100."
        status, payload = self._post_chat(query)
        self.assertEqual(status, 200, payload)
        self.assertIn("PERLU_PERSETUJUAN", payload["answer"])
        self.assertEqual(len(self.providers), 1)
        tool_result = self.providers[0].tool_results[0]
        self.assertTrue(tool_result["ok"], tool_result)
        self.assertEqual(tool_result["program_id"], "budget.threshold.v1")
        self.assertEqual(tool_result["result"], "PERLU_PERSETUJUAN")

        rule = _REGISTERED_RULES["budget.threshold.v1"]
        source = _load_rule_source(rule)
        self.assertEqual(hashlib.sha256(source).hexdigest(), rule["source_sha256"])
        generated = generate(from_source(source.decode("utf-8"), rule["source_file"]))
        with tempfile.TemporaryDirectory(prefix="pusingcuk-ai-e2e-") as temp:
            artifact = Path(temp) / "registered-rule.js"
            artifact.write_text(generated, encoding="utf-8")
            built = subprocess.run(
                [_NODE, str(artifact)],
                input="120\n100\n", text=True, encoding="utf-8",
                capture_output=True, timeout=15, check=False,
            )
        self.assertEqual(built.returncode, 0, built.stderr)
        self.assertEqual(built.stdout, tool_result["result"] + "\n")
        self.assertEqual(self.providers[0].tool_results[0]["program_sha256"], rule["source_sha256"])
    def test_http_path_rejects_model_requested_tool_outside_registry(self):
        self.tool_name = "run_shell"
        self.tool_arguments = {"command": "echo MUST_NOT_RUN"}
        status, payload = self._post_chat("Jalankan perintah shell untuk memeriksa sistem.")

        self.assertEqual(status, 200, payload)
        self.assertIn("tidak terdaftar", payload["answer"])
        provider = self.providers[0]
        offered_names = {
            item["function"]["name"] for item in provider.calls[0]["tools"]
        }
        self.assertNotIn("run_shell", offered_names)
        self.assertEqual(provider.tool_results, [{
            "ok": False,
            "error": "TOOL_NOT_ALLOWLISTED",
        }])
        self.assertEqual(len(provider.calls), 2)


if __name__ == "__main__":
    unittest.main()
