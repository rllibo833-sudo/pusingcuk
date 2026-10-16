"""Tests for internal allowlisted tool and registered .cuk rule bindings."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from compiler.ir import LANGUAGE_VERSION, from_source
from compiler.js_backend import generate
from library.ai_tools import (
    ToolRegistry,
    _REGISTERED_RULES,
    _TOOL_RULE_BINDINGS,
    _load_rule_source,
)


NODE = shutil.which("node")
ROOT = Path(__file__).resolve().parents[1]


class ToolInputContractTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry([])

    def test_cuk_compile_check_compiles_without_executing_or_persisting_source(self):
        source = "jancuk\nlah angka = 40 + 2\nhedeh angka\nselesai jancuk\n"
        result = self.registry.execute("cuk_compile_check", {"source": source})
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["operation"], "compile_check")
        self.assertEqual(result["target"], "javascript")
        self.assertEqual(result["language_version"], LANGUAGE_VERSION)
        self.assertEqual(result["source_sha256"], hashlib.sha256(source.encode("utf-8")).hexdigest())
        self.assertGreater(result["artifact_bytes"], 0)
        self.assertEqual(len(result["artifact_sha256"]), 64)
        self.assertIn('"use strict";', result["artifact"])
        self.assertEqual(
            hashlib.sha256(result["artifact"].encode("utf-8")).hexdigest(),
            result["artifact_sha256"],
        )
        if NODE:
            with tempfile.TemporaryDirectory(prefix="pusingcuk-ai-compiled-") as temp:
                artifact = Path(temp) / "ai-output.js"
                artifact.write_text(result["artifact"], encoding="utf-8")
                executed = subprocess.run(
                    [NODE, str(artifact)], text=True, encoding="utf-8",
                    capture_output=True, timeout=15, check=False,
                )
            self.assertEqual(executed.returncode, 0, executed.stderr)
            self.assertEqual(executed.stdout, "42\n")
        self.assertIs(result["executed"], False)
        self.assertIs(result["artifact_saved"], False)
        definition = next(item["function"] for item in self.registry.definitions
                          if item["function"]["name"] == "cuk_compile_check")
        self.assertEqual(definition["parameters"]["required"], ["source"])
        self.assertIs(definition["parameters"]["additionalProperties"], False)

    def test_cuk_compile_check_rejects_invalid_and_oversized_source(self):
        invalid = self.registry.execute("cuk_compile_check", {"source": "jancuk\nhedeh fungsi_tidak_ada(1)\nselesai jancuk"})
        self.assertFalse(invalid["ok"])
        self.assertEqual(invalid["error"], "CUK_COMPILE_FAILED")
        oversized = self.registry.execute("cuk_compile_check", {"source": "x" * (16 * 1024 + 1)})
        self.assertEqual(oversized, {"ok": False, "error": "CUK_SOURCE_TOO_LARGE"})
        self.assertEqual(
            self.registry.execute("cuk_compile_check", {"source": "jancuk", "target": "shell"}),
            {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"},
        )

    def test_cuk_compile_check_distinguishes_internal_compiler_failure(self):
        with patch("library.ai_tools.generate", side_effect=RuntimeError("internal detail")):
            result = self.registry.execute(
                "cuk_compile_check",
                {"source": "jancuk\nhedeh 42\nselesai jancuk\n"},
            )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "CUK_COMPILER_INTERNAL_ERROR")
        self.assertEqual(result["semantic_review"]["status"], "compiler_internal_error")
        self.assertNotIn("internal detail", result["diagnostic"])
        self.assertIs(result["executed"], False)

    def test_tool_binding_resolves_to_named_registered_rule(self):
        self.assertEqual(_TOOL_RULE_BINDINGS["budget_threshold"], "budget.threshold.v1")
        names = [item["function"]["name"] for item in self.registry.definitions]
        self.assertIn("budget_threshold", names)
        definition = next(item["function"] for item in self.registry.definitions
                          if item["function"]["name"] == "budget_threshold")
        self.assertEqual(definition["parameters"]["required"], ["nominal", "batas"])
        self.assertIs(definition["parameters"]["additionalProperties"], False)

    def test_rule_source_is_packaged_and_hash_pinned(self):
        rule = _REGISTERED_RULES["budget.threshold.v1"]
        source = _load_rule_source(rule)
        self.assertEqual(hashlib.sha256(source).hexdigest(), rule["source_sha256"])
        self.assertIn(b"fungsi status_anggaran(nominal, batas)", source)
        self.assertEqual(rule["capabilities"], ())

    def test_budget_rule_executes_locally_without_legacy_runner_token(self):
        cases = (
            (0, 0, "DALAM_BATAS"),
            (2, 3, "DALAM_BATAS"),
            (3, 3, "DALAM_BATAS"),
            (4, 3, "PERLU_PERSETUJUAN"),
            (0, 1_000_000_000_000, "DALAM_BATAS"),
            (1_000_000_000_000, 0, "PERLU_PERSETUJUAN"),
        )
        with patch.dict(os.environ, {}, clear=True):
            for nominal, batas, expected in cases:
                with self.subTest(nominal=nominal, batas=batas):
                    result = self.registry.execute(
                        "budget_threshold", {"nominal": nominal, "batas": batas}
                    )
                    self.assertTrue(result["ok"], result)
                    self.assertEqual(result["program_id"], "budget.threshold.v1")
                    self.assertEqual(result["result"], expected)
                    self.assertEqual(result["capabilities"], [])
                    self.assertEqual(
                        result["execution_boundary"],
                        "fixed-hash-local-rule-not-os-sandbox",
                    )

    @unittest.skipUnless(NODE, "Node.js tidak tersedia")
    def test_registered_cuk_rule_matches_compiled_javascript_artifact(self):
        rule = _REGISTERED_RULES["budget.threshold.v1"]
        source = _load_rule_source(rule)
        generated = generate(from_source(source.decode("utf-8"), rule["source_file"]))
        cases = ((0, 0, "DALAM_BATAS"), (2, 3, "DALAM_BATAS"), (3, 3, "DALAM_BATAS"), (4, 3, "PERLU_PERSETUJUAN"), (1_000_000_000_000, 0, "PERLU_PERSETUJUAN"))
        with tempfile.TemporaryDirectory(prefix="pusingcuk-ai-artifact-") as temp:
            artifact = Path(temp) / "registered-rule.js"
            artifact.write_text(generated, encoding="utf-8")
            for nominal, batas, expected in cases:
                with self.subTest(nominal=nominal, batas=batas):
                    result = self.registry.execute("budget_threshold", {"nominal": nominal, "batas": batas})
                    compiled = subprocess.run([NODE, str(artifact)], input=f"{nominal}\n{batas}\n", text=True, encoding="utf-8", capture_output=True, timeout=15, check=False)
                    self.assertTrue(result["ok"], result)
                    self.assertEqual(result["result"], expected)
                    self.assertEqual(compiled.returncode, 0, compiled.stderr)
                    self.assertEqual(compiled.stdout, expected + "\n")

    @unittest.skipUnless(NODE, "Node.js tidak tersedia")
    def test_registered_period_close_rule_matches_compiled_javascript_artifact(self):
        """The AI's fixed .cuk closing rule must behave the same in Python and generated JS."""
        rule = _REGISTERED_RULES["period.close.plan.v1"]
        source = _load_rule_source(rule)
        self.assertEqual(hashlib.sha256(source).hexdigest(), rule["source_sha256"])
        generated = generate(from_source(source.decode("utf-8"), rule["source_file"]))

        cases = (
            ("250000", "100000", [
                "PENUTUPAN_LABA", "150000", "250000", "0", "0", "100000", "0", "150000",
            ]),
            ("100000", "250000", [
                "PENUTUPAN_RUGI", "-150000", "100000", "0", "0", "250000", "150000", "0",
            ]),
            ("100000", "100000", [
                "PENUTUPAN_NOL", "0", "100000", "0", "0", "100000", "0", "0",
            ]),
            ("abc", "100", ["INPUT_TIDAK_VALID"]),
        )
        with tempfile.TemporaryDirectory(prefix="pusingcuk-period-close-js-") as temp:
            artifact = Path(temp) / "period-close.js"
            artifact.write_text(generated, encoding="utf-8")
            for income, expense, expected_lines in cases:
                with self.subTest(income=income, expense=expense):
                    stdin_text = f"{income}\n{expense}\n"
                    reference = subprocess.run(
                        [sys.executable, str(ROOT / "pusingcuk_new.py"), str(ROOT / "library" / rule["source_file"])],
                        input=stdin_text, text=True, encoding="utf-8",
                        capture_output=True, timeout=10, cwd=ROOT, check=False,
                    )
                    compiled = subprocess.run(
                        [NODE, str(artifact)], input=stdin_text, text=True, encoding="utf-8",
                        capture_output=True, timeout=10, cwd=ROOT, check=False,
                    )
                    expected = "\n".join(expected_lines) + "\n"
                    self.assertEqual(reference.returncode, 0, reference.stderr)
                    self.assertEqual(compiled.returncode, 0, compiled.stderr)
                    self.assertEqual(reference.stdout, expected)
                    self.assertEqual(compiled.stdout, expected)
                    self.assertEqual(compiled.stdout, reference.stdout)
                    self.assertEqual(compiled.stderr, reference.stderr)


    def test_journal_balance_rule_is_hash_pinned_and_registered(self):
        rule = _REGISTERED_RULES["journal.balance.v1"]
        source = _load_rule_source(rule)
        self.assertEqual(hashlib.sha256(source).hexdigest(), rule["source_sha256"])
        self.assertIn(b"fungsi cek_keseimbangan_jurnal(debit_total, kredit_total)", source)
        self.assertEqual(rule["capabilities"], ())
        self.assertEqual(_TOOL_RULE_BINDINGS["journal_balance_check"], "journal.balance.v1")

    def test_journal_balance_rule_checks_only_positive_totals(self):
        cases = (
            (1250000, 1250000, "JURNAL_SEIMBANG"),
            (1250000, 1249999, "JURNAL_TIDAK_SEIMBANG"),
            (0, 0, "INPUT_TIDAK_VALID"),
            (1, 0, "INPUT_TIDAK_VALID"),
            (1_000_000_000_000, 1_000_000_000_000, "JURNAL_SEIMBANG"),
        )
        for debit_total, kredit_total, expected in cases:
            with self.subTest(debit_total=debit_total, kredit_total=kredit_total):
                result = self.registry.execute(
                    "journal_balance_check",
                    {"debit_total": debit_total, "kredit_total": kredit_total},
                )
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["program_id"], "journal.balance.v1")
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["capabilities"], [])
                self.assertEqual(
                    result["execution_boundary"],
                    "fixed-hash-local-rule-not-os-sandbox",
                )

    def test_cukaccount_period_close_fixture_is_ai_regression_input(self):
        root = Path(__file__).resolve().parents[1]
        fixture = root / "tests" / "conformance" / "cukaccount_financial_cases.cuk"
        completed = subprocess.run(
            [sys.executable, str(root / "pusingcuk_new.py"), str(fixture)],
            cwd=root,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            "\n".join(
                (
                    "CUKACCOUNT_VALID_BALANCED",
                    "CUKACCOUNT_INVALID_UNBALANCED",
                    "CUKACCOUNT_INVALID_ZERO",
                    "CUKACCOUNT_INVALID_NEGATIVE",
                    "CUKACCOUNT_BOUNDARY_MAX",
                )
            ) + "\n",
        )
        self.assertNotIn("CUKACCOUNT_PERIOD_CLOSE_", completed.stdout)

        # Feed the same synthetic closing totals through the AI's fixed .cuk rule.
        for debit_total, credit_total in (
            (250000, 250000),  # profit close
            (250000, 250000),  # loss close
            (100000, 100000),  # zero-result close
        ):
            result = self.registry.execute(
                "journal_balance_check",
                {"debit_total": debit_total, "kredit_total": credit_total},
            )
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["result"], "JURNAL_SEIMBANG")

        mismatch = self.registry.execute(
            "journal_balance_check",
            {"debit_total": 250000, "kredit_total": 249999},
        )
        self.assertTrue(mismatch["ok"], mismatch)
        self.assertEqual(mismatch["result"], "JURNAL_TIDAK_SEIMBANG")

    def test_period_close_plan_matches_shared_cukaccount_acceptance_dataset(self):
        root = Path(__file__).resolve().parents[1]
        dataset_path = root / "tests" / "fixtures" / "cukaccount_financial_acceptance.json"
        dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
        expected = dataset["expected"]
        cases = expected["period_close_cases"]
        self.assertEqual({case["id"] for case in cases}, {"profit", "loss", "zero"})

        for case in cases:
            arguments = {
                "income_total": case["income_total"],
                "expense_total": case["expense_total"],
            }
            with self.subTest(case=case["id"]):
                result = self.registry.execute("period_close_plan", arguments)
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["program_id"], "period.close.plan.v1")
                self.assertEqual(result["result"], case["result"])
                self.assertEqual(result["net_result_minor_units"], case["net_result_minor_units"])
                self.assertEqual(result["debit_total"], case["debit_total"])
                self.assertEqual(result["credit_total"], case["credit_total"])
                self.assertEqual(result["debit_total"], result["credit_total"])
                self.assertEqual(result["closing_lines"], case["closing_lines"])

        profit = next(case for case in cases if case["id"] == "profit")
        expected_account_lines = expected["closing_journal_lines"]
        self.assertEqual(
            [(line["debit"], line["credit"]) for line in expected_account_lines],
            [(line["debit_minor_units"], line["credit_minor_units"]) for line in profit["closing_lines"]],
        )

    def test_period_close_plan_rejects_invalid_values_from_shared_fixture(self):
        root = Path(__file__).resolve().parents[1]
        fixture_path = root / "tests" / "fixtures" / "cukaccount_financial_acceptance.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        cases = fixture["expected"]["period_close_invalid_inputs"]
        for case in cases:
            with self.subTest(input=case["input"]):
                result = self.registry.execute("period_close_plan", case["input"])
                self.assertEqual(
                    result,
                    {"ok": False, "error": case["error"]},
                )

    @unittest.skipUnless(NODE, "Node.js tidak tersedia")
    def test_period_close_rule_matches_compiled_javascript_and_shared_cases(self):
        root = Path(__file__).resolve().parents[1]
        fixture_path = root / "tests" / "fixtures" / "cukaccount_financial_acceptance.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        cases = fixture["expected"]["period_close_cases"]
        rule = _REGISTERED_RULES["period.close.plan.v1"]
        source = _load_rule_source(rule)
        generated = generate(from_source(source.decode("utf-8"), rule["source_file"]))
        with tempfile.TemporaryDirectory(prefix="pusingcuk-period-close-") as temp:
            artifact = Path(temp) / "period-close.js"
            artifact.write_text(generated, encoding="utf-8")
            for case in cases:
                with self.subTest(case=case["id"]):
                    compiled = subprocess.run(
                        [NODE, str(artifact)],
                        input=f'{case["income_total"]}\n{case["expense_total"]}\n',
                        text=True, encoding="utf-8", capture_output=True,
                        timeout=15, check=False,
                    )
                    self.assertEqual(compiled.returncode, 0, compiled.stderr)
                    expected_output = "\n".join(str(value) for value in (
                        case["result"],
                        case["net_result_minor_units"],
                        case["income_total"], 0, 0, case["expense_total"],
                        max(-case["net_result_minor_units"], 0),
                        max(case["net_result_minor_units"], 0),
                    )) + "\n"
                    self.assertEqual(compiled.stdout, expected_output)

    def test_journal_balance_rule_rejects_invalid_arguments(self):
        cases = (
            {"debit_total": 1},
            {"kredit_total": 1},
            {"debit_total": 1, "kredit_total": 2, "command": "id"},
            {"debit_total": True, "kredit_total": 1},
            {"debit_total": -1, "kredit_total": 1},
            {"debit_total": 1_000_000_000_001, "kredit_total": 1},
        )
        for arguments in cases:
            with self.subTest(arguments=arguments):
                expected = (
                    {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
                    if set(arguments) != {"debit_total", "kredit_total"}
                    else {"ok": False, "error": "RULE_INPUT_INVALID"}
                )
                self.assertEqual(
                    self.registry.execute("journal_balance_check", arguments),
                    expected,
                )

    @unittest.skipUnless(NODE, "Node.js tidak tersedia")
    def test_journal_balance_rule_matches_compiled_javascript(self):
        rule = _REGISTERED_RULES["journal.balance.v1"]
        source = _load_rule_source(rule)
        generated = generate(from_source(source.decode("utf-8"), rule["source_file"]))
        cases = (
            (1250000, 1250000, "JURNAL_SEIMBANG"),
            (1250000, 1249999, "JURNAL_TIDAK_SEIMBANG"),
            (0, 0, "INPUT_TIDAK_VALID"),
        )
        with tempfile.TemporaryDirectory(prefix="pusingcuk-ai-journal-rule-") as temp:
            artifact = Path(temp) / "journal-balance.js"
            artifact.write_text(generated, encoding="utf-8")
            for debit_total, kredit_total, expected in cases:
                with self.subTest(debit_total=debit_total, kredit_total=kredit_total):
                    completed = subprocess.run(
                        [NODE, str(artifact)],
                        input=f"{debit_total}\n{kredit_total}\n",
                        text=True,
                        encoding="utf-8",
                        capture_output=True,
                        timeout=15,
                        check=False,
                    )
                    result = self.registry.execute(
                        "journal_balance_check",
                        {"debit_total": debit_total, "kredit_total": kredit_total},
                    )
                    self.assertTrue(result["ok"], result)
                    self.assertEqual(result["result"], expected)
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(completed.stdout, expected + "\n")

    def test_tampered_artifact_fails_closed_before_execution(self):
        with patch("library.ai_tools._load_rule_source", return_value=b"tampered"):
            result = self.registry.execute("budget_threshold", {"nominal": 2, "batas": 3})
        self.assertEqual(result, {"ok": False, "error": "RULE_ARTIFACT_HASH_MISMATCH"})

    def test_missing_artifact_fails_closed(self):
        with patch("library.ai_tools._load_rule_source", side_effect=OSError("missing")):
            result = self.registry.execute("budget_threshold", {"nominal": 2, "batas": 3})
        self.assertEqual(result, {"ok": False, "error": "RULE_ARTIFACT_UNAVAILABLE"})

    def test_runtime_timeout_fails_closed(self):
        with patch(
            "library.ai_tools.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd=["python"], timeout=3),
        ):
            result = self.registry.execute("budget_threshold", {"nominal": 2, "batas": 3})
        self.assertEqual(result, {"ok": False, "error": "RULE_EXECUTION_TIMEOUT"})

    def test_unexpected_rule_output_fails_closed(self):
        completed = subprocess.CompletedProcess(
            args=["python"], returncode=0, stdout="UNEXPECTED\n", stderr=""
        )
        with patch("library.ai_tools.subprocess.run", return_value=completed):
            result = self.registry.execute("budget_threshold", {"nominal": 2, "batas": 3})
        self.assertEqual(result, {"ok": False, "error": "RULE_EXECUTION_FAILED"})

    def test_budget_rule_rejects_wrong_types_and_out_of_range_values_without_execution(self):
        invalid_values = (
            True, False, -1, 1_000_000_000_001, 1.0, "1", None,
        )
        with patch.object(ToolRegistry, "_run_registered_rule") as runner:
            for value in invalid_values:
                for field in ("nominal", "batas"):
                    args = {"nominal": 1, "batas": 1}
                    args[field] = value
                    with self.subTest(field=field, value=repr(value)):
                        self.assertEqual(
                            self.registry.execute("budget_threshold", args),
                            {"ok": False, "error": "RULE_INPUT_INVALID"},
                        )
            runner.assert_not_called()

    def test_budget_rule_rejects_missing_and_extra_fields(self):
        for args in (
            {"nominal": 1},
            {"batas": 1},
            {"nominal": 1, "batas": 2, "command": "id"},
            {"nominal": 1, "batas": 2, "capabilities": ["net.http"]},
        ):
            with self.subTest(args=args):
                self.assertEqual(
                    self.registry.execute("budget_threshold", args),
                    {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"},
                )

    def test_unregistered_platform_capabilities_are_denied_without_side_effects(self):
        forbidden_names = (
            "run_shell", "file_read", "network_fetch", "database_query",
            "execute_sql", "provider_call", "spawn_process",
        )
        for name in forbidden_names:
            with self.subTest(name=name):
                self.assertEqual(
                    self.registry.execute(name, {}),
                    {"ok": False, "error": "TOOL_NOT_ALLOWLISTED"},
                )



    def test_compiler_context_reports_contract_and_real_target_gaps(self):
        result = self.registry.execute("cuk_compiler_context", {"topic": "js"})
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["operation"], "compiler_context")
        self.assertIn("desimal", result["context"]["supported_builtins"])
        self.assertIn("json_teks", result["context"]["supported_builtins"])
        self.assertEqual(result["context"]["unsupported_builtins"], [])

        native = self.registry.execute("cuk_compiler_context", {"topic": "native"})
        self.assertTrue(native["ok"], native)
        self.assertIn("panjang", native["context"]["supported_builtins"])
        self.assertIn("jumlah", native["context"]["supported_builtins"])
        self.assertTrue(native["context"]["required_fixture_ids"])
        self.assertIn("unsupported_fixture_ids", native["context"])
        self.assertTrue(native["context"]["shared_required_fixture_ids"])
        self.assertTrue(native["context"]["reference_only_fixture_ids"])
        self.assertEqual(
            set(native["context"]["shared_required_fixture_ids"]),
            set(native["context"]["shared_required_fixture_ids"]) & set(native["context"]["required_fixture_ids"]),
        )

        development = self.registry.execute("cuk_compiler_context", {"topic": "development"})
        self.assertTrue(development["ok"], development)
        self.assertIn("jumlah", " ".join(development["context"]["priority_semantics"]))
        self.assertIn("compile success is not runtime proof", " ".join(development["context"]["guardrails"]))
        self.assertTrue(development["context"]["shared_required_fixture_ids"])
        self.assertTrue(development["context"]["next_actions"])

        formats = self.registry.execute("cuk_compiler_context", {"topic": "formats"})
        self.assertEqual({item["name"] for item in formats["context"]["builtins"]},
                         {"json_teks", "json_baca", "html_aman", "csv_baris"})

        invalid = self.registry.execute("cuk_compiler_context", {"topic": "not-a-topic"})
        self.assertEqual(invalid, {"ok": False, "error": "COMPILER_CONTEXT_TOPIC_INVALID"})

if __name__ == "__main__":
    unittest.main()
