"""Regression tests for the bounded Gemini GenerateContent adapter."""
import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from library.gemini_ai_provider import GeminiGenerateContentProvider
from library.local_ai_provider import LocalAIProviderError


class FakeResponse:
    status = 200

    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, limit=-1):
        return self.body[:limit]


class GeminiProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = GeminiGenerateContentProvider("test-api-key-123456", model="gemini-test")
        self.messages = [{"role": "user", "content": "Jelaskan PusingCuk dalam bahasa Indonesia."}]

    def test_https_key_header_system_prompt_and_text(self):
        body = json.dumps({"candidates": [{"content": {"parts": [{"text": "PusingCuk adalah bahasa."}]}}]}).encode()
        with patch("library.gemini_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(body)
            answer = self.provider.generate(self.messages, system_prompt="Jawab jujur.")
        self.assertEqual(answer, "PusingCuk adalah bahasa.")
        request = builder.return_value.open.call_args.args[0]
        self.assertEqual(request.full_url, "https://generativelanguage.googleapis.com/v1beta/models/gemini-test:generateContent")
        self.assertEqual(request.get_header("X-goog-api-key"), "test-api-key-123456")
        self.assertNotIn("test-api-key-123456", request.full_url)
        payload = json.loads(request.data.decode())
        self.assertEqual(payload["systemInstruction"]["parts"][0]["text"], "Jawab jujur.")

    def test_function_call_schema_is_mapped(self):
        body = json.dumps({"candidates": [{"content": {"parts": [{"functionCall": {"id": "call-1", "name": "knowledge_search", "args": {"query": "ollama lokal", "limit": 2}}}]}}]}).encode()
        with patch("library.gemini_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(body)
            turn = self.provider.generate_turn(self.messages, tools=[{"type": "function", "function": {"name": "knowledge_search", "description": "Cari dokumen", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False}}}])
        self.assertEqual(turn["tool_calls"][0]["name"], "knowledge_search")
        payload = json.loads(builder.return_value.open.call_args.args[0].data.decode())
        self.assertEqual(payload["tools"][0]["functionDeclarations"][0]["name"], "knowledge_search")

    def test_tool_history_maps_to_function_response(self):
        history = [
            {"role": "user", "content": "Cari sumber."},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "call-1", "type": "function", "function": {"name": "knowledge_search", "arguments": {"query": "pusingcuk"}}}]},
            {"role": "tool", "tool_name": "knowledge_search", "content": '{"ok": true, "result_count": 1}'},
        ]
        body = json.dumps({"candidates": [{"content": {"parts": [{"text": "Sumber ditemukan."}]}}]}).encode()
        with patch("library.gemini_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(body)
            turn = self.provider.generate_turn(history)
        self.assertEqual(turn["content"], "Sumber ditemukan.")
        payload = json.loads(builder.return_value.open.call_args.args[0].data.decode())
        self.assertEqual(payload["contents"][-1]["role"], "user")
        self.assertEqual(payload["contents"][-1]["parts"][0]["functionResponse"]["name"], "knowledge_search")

    def test_invalid_configuration_is_rejected(self):
        with self.assertRaisesRegex(LocalAIProviderError, "API_KEY_INVALID"):
            GeminiGenerateContentProvider("")
        with self.assertRaisesRegex(LocalAIProviderError, "MODEL_INVALID"):
            GeminiGenerateContentProvider("test-api-key-123456", model="../bad")

    def test_more_than_two_function_calls_are_rejected(self):
        parts = [{"functionCall": {"name": "knowledge_search", "args": {"query": str(i)}}} for i in range(3)]
        body = json.dumps({"candidates": [{"content": {"parts": parts}}]}).encode()
        with patch("library.gemini_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(body)
            with self.assertRaisesRegex(LocalAIProviderError, "TOOL_CALLS_INVALID"):
                self.provider.generate_turn(self.messages)

    def test_network_failure_is_sanitized(self):
        with patch("library.gemini_ai_provider.build_opener") as builder:
            builder.return_value.open.side_effect = URLError("private endpoint detail")
            with self.assertRaisesRegex(LocalAIProviderError, "PROVIDER_UNAVAILABLE") as error:
                self.provider.generate(self.messages)
        self.assertNotIn("private endpoint detail", str(error.exception))


if __name__ == "__main__":
    unittest.main()
