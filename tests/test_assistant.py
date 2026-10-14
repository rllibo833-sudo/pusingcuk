"""Regression tests for PusingCuk's local-first RAG chat orchestration."""
import unittest
from pathlib import Path

from library.assistant import PusingCukAssistant
from library.knowledge_grounding import load_index
from library.local_ai_provider import LocalAIProviderError


class FakeProvider:
    def __init__(self, answer="Jawaban berdasarkan dokumen."):
        self.answer = answer
        self.calls = []

    def generate(self, messages, *, system_prompt=None):
        self.calls.append({"messages": messages, "system_prompt": system_prompt})
        return self.answer


class AssistantTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "library" / "knowledge_index.json"
        self.documents = load_index(path)
        self.provider = FakeProvider()
        self.assistant = PusingCukAssistant(self.provider, self.documents)

    def test_retrieves_context_and_appends_verified_citations(self):
        answer = self.assistant.ask("Apa arah model lokal Ollama tanpa biaya API?")
        self.assertIn("LOCAL", self.provider.calls[0]["system_prompt"].upper())
        self.assertIn("Sumber rujukan", answer)
        self.assertIn("38ad3035af7e7eaba8a332656ab6155dcc313c72", answer)

    def test_unmatched_query_does_not_invent_source_citation(self):
        answer = self.assistant.ask("zebra xylophone nebula")
        self.assertNotIn("Sumber rujukan", answer)

    def test_conversation_context_is_reused_in_memory(self):
        self.assistant.ask("Apa itu PusingCuk?")
        self.assistant.ask("Jelaskan lagi dengan ringkas")
        self.assertEqual(len(self.assistant.history), 4)
        self.assertEqual(self.provider.calls[1]["messages"][-2]["role"], "assistant")

    def test_reset_clears_ephemeral_conversation(self):
        self.assistant.ask("Apa itu PusingCuk?")
        self.assistant.reset()
        self.assertEqual(self.assistant.history, [])

    def test_invalid_query_is_rejected_before_provider_call(self):
        with self.assertRaisesRegex(ValueError, "AI_QUERY_INVALID"):
            self.assistant.ask(" ")
        self.assertEqual(self.provider.calls, [])

    def test_provider_failure_does_not_store_failed_turn(self):
        class BrokenProvider:
            def generate(self, *_args, **_kwargs):
                raise LocalAIProviderError("AI_TIMEOUT")
        assistant = PusingCukAssistant(BrokenProvider(), self.documents)
        with self.assertRaisesRegex(LocalAIProviderError, "AI_TIMEOUT"):
            assistant.ask("Apa itu PusingCuk?")
        self.assertEqual(assistant.history, [])


if __name__ == "__main__":
    unittest.main()
