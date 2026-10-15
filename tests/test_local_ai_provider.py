"""Regression tests for the bounded, loopback-only local model adapter."""
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from library.local_ai_provider import LocalAIProviderError, OllamaChatProvider, validate_messages


class FakeResponse:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, limit=-1):
        return self.body[:limit]


class LocalAIProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = OllamaChatProvider(model="qwen3:4b")
        self.messages = [{"role": "user", "content": "Jelaskan PusingCuk dalam bahasa Indonesia."}]

    def test_sends_non_streaming_chat_and_returns_text(self):
        body = json.dumps({"message": {"role": "assistant", "content": "PusingCuk adalah bahasa."}}).encode()
        with patch("library.local_ai_provider.build_opener") as mocked_builder:
            mocked = mocked_builder.return_value
            mocked.open.return_value = FakeResponse(body)
            result = self.provider.generate(self.messages)
        self.assertEqual(result, "PusingCuk adalah bahasa.")
        request = mocked.open.call_args.args[0]
        payload = json.loads(request.data.decode())
        self.assertEqual(payload["model"], "qwen3:4b")
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["messages"], self.messages)

    def test_system_prompt_is_inserted_before_user_message(self):
        body = json.dumps({"message": {"content": "Siap."}}).encode()
        with patch("library.local_ai_provider.build_opener") as mocked_builder:
            mocked = mocked_builder.return_value
            mocked.open.return_value = FakeResponse(body)
            self.provider.generate(self.messages, system_prompt="Jawab ringkas dan jujur.")
        payload = json.loads(mocked.open.call_args.args[0].data.decode())
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][0]["content"], "Jawab ringkas dan jujur.")

    def test_remote_endpoint_is_rejected_by_default(self):
        with self.assertRaisesRegex(LocalAIProviderError, "NOT_LOOPBACK"):
            OllamaChatProvider(endpoint="http://192.168.1.20:11434")

    def test_invalid_roles_and_extra_message_fields_are_rejected(self):
        for message in ({"role": "tool", "content": "x"}, {"role": "user", "content": "x", "secret": "y"}):
            with self.subTest(message=message), self.assertRaises(LocalAIProviderError):
                validate_messages([message])

    def test_user_message_is_required(self):
        with self.assertRaisesRegex(LocalAIProviderError, "USER_MESSAGE_REQUIRED"):
            validate_messages([{"role": "system", "content": "Ikuti kontrak."}])

    def test_message_and_context_limits_are_enforced(self):
        with self.assertRaisesRegex(LocalAIProviderError, "MESSAGE_TOO_LARGE"):
            validate_messages([{"role": "user", "content": "x" * 12_001}])
        with self.assertRaisesRegex(LocalAIProviderError, "MESSAGE_COUNT_INVALID"):
            validate_messages([{"role": "user", "content": "x"}] * 21)

    def test_oversized_response_is_rejected(self):
        provider = OllamaChatProvider(max_response_bytes=1024)
        body = b" " * 1025
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(body)
            with self.assertRaisesRegex(LocalAIProviderError, "RESPONSE_TOO_LARGE"):
                provider.generate(self.messages)

    def test_invalid_json_and_missing_content_are_rejected(self):
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(b"not-json")
            with self.assertRaisesRegex(LocalAIProviderError, "INVALID_JSON"):
                self.provider.generate(self.messages)
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(b'{"message":{}}')
            with self.assertRaisesRegex(LocalAIProviderError, "CONTENT_MISSING"):
                self.provider.generate(self.messages)

    def test_network_failure_returns_stable_error_without_url_details(self):
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.side_effect = URLError("sensitive endpoint detail")
            with self.assertRaisesRegex(LocalAIProviderError, "PROVIDER_UNAVAILABLE") as error:
                self.provider.generate(self.messages)
        self.assertNotIn("sensitive", str(error.exception))

    def test_generate_turn_parses_a_bounded_tool_call(self):
        body = json.dumps({"message": {"content": "", "tool_calls": [{"id": "call-1", "function": {"name": "knowledge_search", "arguments": {"query": "ollama lokal"}}}]}}).encode()
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(body)
            turn = self.provider.generate_turn(self.messages, tools=[{"type": "function", "function": {"name": "knowledge_search"}}])
        self.assertEqual(turn["content"], "")
        self.assertEqual(turn["tool_calls"][0]["name"], "knowledge_search")
        self.assertEqual(turn["tool_calls"][0]["arguments"], {"query": "ollama lokal"})

    def test_gemini_signature_metadata_is_not_sent_to_ollama(self):
        history = self.messages + [
            {"role": "assistant", "content": "", "tool_calls": [{
                "id": "call-1", "type": "function",
                "function": {"name": "knowledge_search", "arguments": {"query": "pusingcuk"}},
                "thought_signature": "opaque-signature-test",
            }]},
            {"role": "tool", "tool_name": "knowledge_search", "content": "{}"},
        ]
        body = json.dumps({"message": {"content": "Sumber ditemukan."}}).encode()
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(body)
            self.provider.generate_turn(history)
        payload = json.loads(builder.return_value.open.call_args.args[0].data.decode())
        outbound_call = payload["messages"][1]["tool_calls"][0]
        self.assertNotIn("thought_signature", outbound_call)
        self.assertEqual(outbound_call["function"]["name"], "knowledge_search")

    def test_tool_history_message_is_validated(self):
        history = self.messages + [
            {"role": "assistant", "content": "", "tool_calls": [{"id": "call-1", "type": "function", "function": {"name": "knowledge_search", "arguments": {"query": "ollama lokal"}}}]},
            {"role": "tool", "tool_name": "knowledge_search", "content": "{}"},
        ]
        self.assertEqual(validate_messages(history)[-1]["tool_name"], "knowledge_search")

    def test_more_than_two_tool_calls_are_rejected(self):
        body = json.dumps({"message": {"content": "", "tool_calls": [
            {"function": {"name": "knowledge_search", "arguments": {"query": "a"}}},
            {"function": {"name": "knowledge_search", "arguments": {"query": "b"}}},
            {"function": {"name": "knowledge_search", "arguments": {"query": "c"}}},
        ]}}).encode()
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.return_value = FakeResponse(body)
            with self.assertRaisesRegex(LocalAIProviderError, "TOOL_CALLS_INVALID"):
                self.provider.generate_turn(self.messages)


    def test_rate_limit_is_normalized_and_provider_body_is_not_exposed(self):
        failure = HTTPError("https://provider.invalid", 429, "quota exceeded - private detail", None, None)
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.side_effect = failure
            with self.assertRaisesRegex(LocalAIProviderError, "AI_PROVIDER_RATE_LIMITED") as error:
                self.provider.generate(self.messages)
        self.assertNotIn("private detail", str(error.exception))

    def test_timeout_is_normalized(self):
        with patch("library.local_ai_provider.build_opener") as builder:
            builder.return_value.open.side_effect = TimeoutError("sensitive timeout detail")
            with self.assertRaisesRegex(LocalAIProviderError, "AI_TIMEOUT") as error:
                self.provider.generate(self.messages)
        self.assertNotIn("sensitive", str(error.exception))


if __name__ == "__main__":
    unittest.main()
