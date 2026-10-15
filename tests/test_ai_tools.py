"""Tests for internal allowlisted tool and registered .cuk rule bindings."""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from compiler.ir import from_source
from compiler.js_backend import generate
from library.ai_tools import (
    ToolRegistry,
    _REGISTERED_RULES,
    _TOOL_RULE_BINDINGS,
    _load_rule_source,
)


NODE = shutil.which("node")


class ToolInputContractTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry([])

    def test_cuk_compile_check_compiles_without_executing_or_persisting_source(self):
        source = "jancuk\nlah angka = 40 + 2\nhedeh angka\nselesai jancuk\n"
        result = self.registry.execute("cuk_compile_check", {"source": source})
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["operation"], "compile_check")
        self.assertEqual(result["target"], "javascript")
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


if __name__ == "__main__":
    unittest.main()
