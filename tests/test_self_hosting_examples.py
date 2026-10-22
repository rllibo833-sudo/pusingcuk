"""Runtime smoke tests for the staged .cuk self-hosting prototypes."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"
EXAMPLES = ROOT / "examples" / "self_hosting"


class SelfHostingExampleTests(unittest.TestCase):
    def run_example(self, filename: str, expected: str) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), str(EXAMPLES / filename)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected)

    def test_lexer_token_classifier(self) -> None:
        self.run_example(
            "lexer.cuk", "OP_PLUS\nOP_MINUS\nLITERAL_OR_UNKNOWN\n"
        )

    def test_source_lexer_scans_source_text(self) -> None:
        payload = {
            "source_name": "lexer_smoke.cuk",
            "source": "lah x = 12 + 3\\nhedeh x\\n",
        }
        result = subprocess.run(
            [sys.executable, str(CLI), str(EXAMPLES / "compiler.cuk")],
            cwd=ROOT,
            input=json.dumps(payload),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stderr, "")
        document = json.loads(result.stdout)
        self.assertEqual(document["format"], "pusingcuk-ir")
        self.assertEqual(document["ir_version"], 1)
        self.assertEqual(document["source_name"], "lexer_smoke.cuk")
        self.assertIn("operators", document["features"])

    def test_parser_builds_arithmetic_node(self) -> None:
        self.run_example(
            "parser.cuk",
            "OK\n7\n+\n35\nSOURCE_OK\n7\n+\n35\nPARSE_ERROR\n",
        )

    def test_evaluator_computes_node(self) -> None:
        self.run_example("evaluator.cuk", "42\n")

    def test_mini_interpreter_pipeline(self) -> None:
        self.run_example("interpreter.cuk", "Status parse: OK\nHasil: 42\n")

    def test_codegen_emits_target_text(self) -> None:
        self.run_example("codegen.cuk", "long hasil = (7 + (5 * 6));\nUNSUPPORTED_OPERATOR\n")

    def test_runtime_contract_reports_evidence_state(self) -> None:
        self.run_example(
            "runtime_contract.cuk",
            "VERIFIED_FOR_THIS_TARGET\nNOT_YET_VERIFIED\nUNSUPPORTED\n",
        )


if __name__ == "__main__":
    unittest.main()
