"""Integration tests for the localhost Studio HTTP bridge."""
from __future__ import annotations

import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from library import studio_service


class FakeAssistant:
    def ask(self, query):
        return "PusingCuk AI menjawab: " + query


class StudioServiceTests(unittest.TestCase):
    def setUp(self):
        self.server = studio_service._Server(("127.0.0.1", 0), studio_service._Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:" + str(self.server.server_address[1])

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def request(self, path, payload=None):
        headers = {}
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")
        req = Request(self.base + path, data=data, headers=headers)
        try:
            with urlopen(req, timeout=10) as response:
                return response.status, response.headers.get_content_type(), response.read()
        except HTTPError as exc:
            return exc.code, exc.headers.get_content_type(), exc.read()

    def test_health_and_html_are_served_from_same_origin(self):
        status, content_type, body = self.request("/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"ok": True, "runtime": "python-reference", "ai": "ollama-configured"})
        status, content_type, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/html")
        self.assertIn(b"PusingCuk", body)

    def test_chat_calls_pusingcuk_assistant(self):
        with patch.object(studio_service, "_assistant", return_value=FakeAssistant()):
            status, _, body = self.request("/api/chat", {"query": "bantu .cuk"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["answer"], "PusingCuk AI menjawab: bantu .cuk")

    def test_run_executes_reference_runtime(self):
        source = "jancuk\nhedeh 40 + 2\nselesai jancuk"
        status, _, body = self.request("/api/run", {"source": source, "stdin": ""})
        result = json.loads(body)
        self.assertEqual(status, 200)
        self.assertTrue(result["ok"], result)
        self.assertIn("42", result["stdout"])

    def test_invalid_chat_query_is_rejected(self):
        status, _, body = self.request("/api/chat", {"query": " "})
        self.assertEqual(status, 400)
        self.assertEqual(json.loads(body)["error"], "QUERY_INVALID")


if __name__ == "__main__":
    unittest.main()
