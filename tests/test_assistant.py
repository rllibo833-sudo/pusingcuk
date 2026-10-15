"""Regression tests for PusingCuk's local-first RAG and tool orchestration."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from library.ai_tools import ToolRegistry
from library.assistant import PusingCukAssistant
from library.knowledge_grounding import load_index
from library.local_ai_provider import LocalAIProviderError
from library.local_memory import LocalMemoryStore
import tempfile


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
        self.assertIn("PusingCuk AI", self.provider.calls[0]["system_prompt"])
        self.assertIn(".cuk", self.provider.calls[0]["system_prompt"])
        self.assertIn("bukan klaim bahwa model dasar dilatih sendiri", self.provider.calls[0]["system_prompt"])
        self.assertIn("LOCAL", self.provider.calls[0]["system_prompt"].upper())
        self.assertIn("Sumber rujukan", answer)
        self.assertIn("733d4328a8d4433b1633e8d3bba9601786c2e08a", answer)

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

    def test_explicit_local_memory_is_retrieved_as_context(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LocalMemoryStore(Path(directory) / "memory.json")
            store.remember("PusingCuk adalah repositori utama; Founder OS dan CORE dibekukan setelah migrasi.", confirmed=True)
            assistant = PusingCukAssistant(self.provider, self.documents, memory_store=store)
            assistant.ask("Apa keputusan repositori utama PusingCuk?")
            prompt = self.provider.calls[0]["system_prompt"]
            self.assertIn("Catatan proyek yang disimpan", prompt)
            self.assertIn("Founder OS dan CORE dibekukan", prompt)

    def test_chat_does_not_persist_memory_without_explicit_command(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.json"
            assistant = PusingCukAssistant(self.provider, self.documents, memory_store=LocalMemoryStore(path))
            assistant.ask("Apa itu PusingCuk?")
            self.assertFalse(path.exists())

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

    def test_tool_call_executes_only_allowlisted_knowledge_search(self):
        class ToolProvider:
            def __init__(self):
                self.calls = []
            def generate_turn(self, messages, *, system_prompt=None, tools=None):
                self.calls.append({"messages": messages, "tools": tools})
                if len(self.calls) == 1:
                    return {"content": "", "tool_calls": [{"id": "call-1", "name": "knowledge_search", "arguments": {"query": "ollama lokal", "limit": 2}}]}
                return {"content": "Arah yang ditemukan mengutamakan model lokal.", "tool_calls": []}
        provider = ToolProvider()
        assistant = PusingCukAssistant(provider, self.documents)
        answer = assistant.ask("zebra xylophone nebula")
        self.assertEqual(len(provider.calls), 2)
        self.assertTrue(any(m["role"] == "tool" for m in provider.calls[1]["messages"]))
        self.assertIn("Sumber rujukan", answer)

    def test_assistant_rejects_over_limit_tool_calls_before_execution(self):
        class OversizedToolProvider:
            def generate_turn(self, messages, *, system_prompt=None, tools=None):
                return {"content": "", "tool_calls": [
                    {"id": f"call-{i}", "name": "budget_threshold", "arguments": {"nominal": 10, "batas": 20}}
                    for i in range(3)
                ]}

        assistant = PusingCukAssistant(OversizedToolProvider(), self.documents)
        with patch.object(ToolRegistry, "_run_registered_rule") as runner:
            with self.assertRaisesRegex(LocalAIProviderError, "AI_TOOL_CALLS_INVALID"):
                assistant.ask("Periksa tiga aturan anggaran sekaligus")
            runner.assert_not_called()

    def test_model_request_for_unregistered_tool_is_rejected_in_assistant_loop(self):
        class MaliciousProvider:
            def __init__(self):
                self.calls = 0
            def generate_turn(self, messages, *, system_prompt=None, tools=None):
                self.calls += 1
                if self.calls == 1:
                    return {"content": "", "tool_calls": [
                        {"id": "attack-1", "name": "run_shell", "arguments": {"command": "touch SHOULD_NOT_EXIST"}}
                    ]}
                tool_messages = [m for m in messages if m["role"] == "tool"]
                self.assert_error = json.loads(tool_messages[-1]["content"])
                return {"content": "Permintaan tool ditolak.", "tool_calls": []}

        provider = MaliciousProvider()
        assistant = PusingCukAssistant(provider, self.documents)
        answer = assistant.ask("Jalankan perintah shell")
        self.assertEqual(provider.calls, 2)
        self.assertEqual(provider.assert_error, {"ok": False, "error": "TOOL_NOT_ALLOWLISTED"})
        self.assertIn("Permintaan tool ditolak", answer)
        self.assertFalse(Path("SHOULD_NOT_EXIST").exists())

    def test_tool_result_is_cited_and_model_link_is_not_trusted(self):
        class ToolProvider:
            def __init__(self):
                self.calls = 0
            def generate_turn(self, messages, *, system_prompt=None, tools=None):
                self.calls += 1
                if self.calls == 1:
                    return {"content": "", "tool_calls": [
                        {"id": "lookup-1", "name": "knowledge_search", "arguments": {"query": "ollama lokal", "limit": 2}}
                    ]}
                return {"content": "Model lokal dijalankan terpisah. Rujukan lain: https://untrusted.invalid/source", "tool_calls": []}

        provider = ToolProvider()
        assistant = PusingCukAssistant(provider, self.documents)
        answer = assistant.ask("Tolong cari sumber tentang Ollama lokal.")
        self.assertEqual(provider.calls, 2)
        self.assertIn("Sumber rujukan", answer)
        self.assertIn("github.com/rllibo833-sudo/", answer)
        self.assertNotIn("untrusted.invalid", answer)

    def test_tool_registry_rejects_unregistered_names_and_invalid_rule_input(self):
        registry = ToolRegistry(self.documents)
        self.assertEqual(registry.execute("run_shell", {"command": "id"})["error"], "TOOL_NOT_ALLOWLISTED")
        self.assertEqual(registry.execute("budget_threshold", {"nominal": True, "batas": 100})["error"], "RULE_INPUT_INVALID")

    def test_budget_rule_executes_without_runner_token(self):
        registry = ToolRegistry(self.documents)
        with patch.dict("os.environ", {}, clear=True):
            result = registry.execute("budget_threshold", {"nominal": 10, "batas": 20})
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["result"], "DALAM_BATAS")
        self.assertEqual(result["program_id"], "budget.threshold.v1")
        self.assertEqual(result["capabilities"], [])

    def test_registered_budget_rule_boundary_cases_execute_with_verified_sources(self):
        class BudgetToolProvider:
            def __init__(self, nominal, batas):
                self.nominal = nominal
                self.batas = batas
                self.calls = 0

            def generate_turn(self, messages, *, system_prompt=None, tools=None):
                self.calls += 1
                if self.calls == 1:
                    return {
                        "content": "",
                        "tool_calls": [{
                            "id": "budget-boundary",
                            "name": "budget_threshold",
                            "arguments": {"nominal": self.nominal, "batas": self.batas},
                        }],
                    }
                return {"content": "Aturan anggaran lokal selesai.", "tool_calls": []}

        cases = [
            (0, 0, "DALAM_BATAS"),
            (100, 100, "DALAM_BATAS"),
            (101, 100, "PERLU_PERSETUJUAN"),
            (1_000_000_000_000, 1_000_000_000_000, "DALAM_BATAS"),
        ]
        for nominal, batas, expected in cases:
            with self.subTest(nominal=nominal, batas=batas):
                provider = BudgetToolProvider(nominal, batas)
                assistant = PusingCukAssistant(provider, self.documents)
                answer = assistant.ask(f"Periksa anggaran {nominal} dengan batas {batas}.")
                self.assertEqual(provider.calls, 2)
                self.assertIn("Aturan anggaran lokal selesai", answer)
                self.assertIn("Sumber rujukan", answer)
                urls = __import__("re").findall(r"\]\((https://[^)]+)\)", answer)
                self.assertTrue(urls)
                known_urls = {doc["url"] for doc in self.documents}
                self.assertTrue(set(urls) <= known_urls)
                self.assertNotIn("untrusted", answer.lower())

    def test_budget_rule_assistant_tool_call_uses_internal_registry_binding(self):
        class BudgetToolProvider:
            def __init__(self):
                self.calls = 0

            def generate_turn(self, messages, *, system_prompt=None, tools=None):
                self.calls += 1
                if self.calls == 1:
                    return {
                        "content": "",
                        "tool_calls": [{
                            "id": "budget-1",
                            "name": "budget_threshold",
                            "arguments": {"nominal": 100, "batas": 200},
                        }],
                    }
                return {"content": "Pengecekan lokal selesai.", "tool_calls": []}

        provider = BudgetToolProvider()
        assistant = PusingCukAssistant(provider, self.documents)
        with patch.object(
            ToolRegistry,
            "_run_registered_rule",
            return_value={
                "ok": True,
                "program_id": "budget.threshold.v1",
                "result": "DALAM_BATAS",
                "capabilities": [],
                "execution_boundary": "fixed-hash-local-rule-not-os-sandbox",
            },
        ) as runner:
            answer = assistant.ask("Periksa anggaran 100 dengan batas 200.")
        runner.assert_called_once_with(
            "budget.threshold.v1", {"nominal": 100, "batas": 200}
        )
        self.assertIn("Pengecekan lokal selesai", answer)

    def test_internal_registry_rejects_rule_ids_as_unregistered_tool_names(self):
        registry = ToolRegistry(self.documents)
        self.assertEqual(
            registry.execute("budget.threshold.v1", {"nominal": 10, "batas": 20}),
            {"ok": False, "error": "TOOL_NOT_ALLOWLISTED"},
        )


if __name__ == "__main__":
    unittest.main()
