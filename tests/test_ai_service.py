"""HTTP contract/security regression tests for the local PusingCuk AI service."""
from __future__ import annotations

import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from library.ai_service import MAX_REQUEST_BYTES, create_server

TOKEN = "test-service-token-" + ("x" * 40)


class FakeAssistant:
    def __init__(self):
        self.queries = []

    def ask(self, query):
        self.queries.append(query)
        if query == "__provider_failure__":
            raise RuntimeError("do not leak provider details")
        return "Jawaban uji: " + query


class AIServiceTests(unittest.TestCase):
    def setUp(self):
        self.assistants = []

        def factory():
            assistant = FakeAssistant()
            self.assistants.append(assistant)
            return assistant

        self.server = create_server("127.0.0.1", 0, token=TOKEN, assistant_factory=factory)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = "http://127.0.0.1:" + str(self.server.server_address[1])

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def request(self, path="/v1/chat", *, payload=None, token=TOKEN, raw=None, headers=None, method="POST"):
        body = raw if raw is not None else json.dumps(
            payload if payload is not None else {"session_id": "session_0123456789", "query": "uji"},
        ).encode("utf-8")
        if isinstance(body, str):
            body = body.encode("utf-8")
        request_headers = {"Content-Type": "application/json"}
        if token is not None:
            request_headers["Authorization"] = "Bearer " + token
        request_headers.update(headers or {})
        req = Request(self.base_url + path, data=body if method != "GET" else None,
                      headers=request_headers, method=method)
        try:
            with urlopen(req, timeout=3) as response:
                return response.status, json.loads(response.read().decode("utf-8")), response.headers
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8")), exc.headers

    def test_health_is_minimal_liveness_only(self):
        status, payload, _ = self.request("/healthz", method="GET", token=None)
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ok"})

    def test_chat_requires_bearer_token(self):
        status, payload, headers = self.request(token=None)
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "AI_SERVICE_UNAUTHORIZED")
        self.assertEqual(headers.get("Cache-Control"), "no-store")
        self.assertFalse(self.assistants)

    def test_valid_chat_reuses_only_its_ephemeral_session(self):
        first_status, first, _ = self.request(payload={"session_id": "session_0123456789", "query": "pertama"})
        second_status, second, _ = self.request(payload={"session_id": "session_0123456789", "query": "kedua"})
        self.assertEqual((first_status, second_status), (200, 200))
        self.assertNotEqual(first["request_id"], second["request_id"])
        self.assertEqual(first["session_id"], "session_0123456789")
        self.assertEqual(len(self.assistants), 1)
        self.assertEqual(self.assistants[0].queries, ["pertama", "kedua"])

    def test_sessions_do_not_share_assistant_history(self):
        self.assertEqual(self.request(payload={"session_id": "session_AAAAAAAAAA", "query": "A"})[0], 200)
        self.assertEqual(self.request(payload={"session_id": "session_BBBBBBBBBB", "query": "B"})[0], 200)
        self.assertEqual(len(self.assistants), 2)
        self.assertEqual(self.assistants[0].queries, ["A"])
        self.assertEqual(self.assistants[1].queries, ["B"])

    def test_invalid_json_and_duplicate_keys_are_rejected(self):
        status, payload, _ = self.request(raw="{")
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "AI_SERVICE_JSON_INVALID")
        raw = '{"session_id":"session_0123456789","query":"a","query":"b"}'
        status, payload, _ = self.request(raw=raw)
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "AI_SERVICE_JSON_INVALID")

    def test_schema_session_and_query_are_bounded(self):
        status, payload, _ = self.request(payload={"session_id": "short", "query": "uji"})
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "AI_SERVICE_SESSION_ID_INVALID")
        status, payload, _ = self.request(payload={"session_id": "session_0123456789", "query": " "})
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "AI_SERVICE_QUERY_INVALID")
        status, payload, _ = self.request(payload={"session_id": "session_0123456789", "query": "x" * 301})
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "AI_SERVICE_QUERY_INVALID")

    def test_oversized_and_unexpected_payload_fields_are_rejected(self):
        status, payload, _ = self.request(raw=b"x" * (MAX_REQUEST_BYTES + 1))
        self.assertEqual(status, 413)
        self.assertEqual(payload["error"], "AI_SERVICE_REQUEST_TOO_LARGE")
        status, payload, _ = self.request(payload={"session_id": "session_0123456789", "query": "uji", "tool": "shell"})
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "AI_SERVICE_REQUEST_SCHEMA_INVALID")

    def test_provider_errors_do_not_leak_exception_details(self):
        status, payload, _ = self.request(payload={"session_id": "session_0123456789", "query": "__provider_failure__"})
        self.assertEqual(status, 502)
        self.assertEqual(payload["error"], "AI_SERVICE_PROVIDER_FAILURE")
        self.assertNotIn("do not leak", json.dumps(payload))

    def test_non_loopback_binding_is_refused(self):
        with self.assertRaisesRegex(ValueError, "AI_SERVICE_BIND_MUST_BE_LOOPBACK"):
            create_server("0.0.0.0", 0, token=TOKEN, assistant_factory=FakeAssistant)

    def test_weak_service_token_is_refused(self):
        with self.assertRaisesRegex(ValueError, "AI_SERVICE_TOKEN_REQUIRED"):
            create_server("127.0.0.1", 0, token="weak", assistant_factory=FakeAssistant)


if __name__ == "__main__":
    unittest.main()
