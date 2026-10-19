import json
import tempfile
import unittest
from pathlib import Path

from compiler.repair_loop import RepairLoop


class Adapter:
    def __init__(self, proposal):
        self.proposal = proposal

    def propose(self, request, current_source, diagnostics):
        return self.proposal


class RepairLoopTests(unittest.TestCase):
    def make_loop(self, td, proposal, fixture, matrix, compiler=None):
        return RepairLoop(
            Adapter(proposal),
            compiler=compiler or (lambda source: {"ok": True}),
            fixture_runner=lambda source, fixture_id: fixture,
            differential_runner=lambda source: matrix,
            log_path=Path(td) / "attempts.jsonl",
        )

    def test_accept_requires_new_fixture_and_complete_clean_matrix(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self.make_loop(td, "fixed", {"added": True, "fixture_id": "F-1"},
                                  {"ok": True, "complete": True, "regressions": []})
            result = loop.attempt("fix bug", "broken")
            self.assertTrue(result.accepted)
            self.assertEqual(result.fixture_id, "F-1")

    def test_rejects_without_new_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self.make_loop(td, "fixed", {"added": False},
                                  {"ok": True, "complete": True, "regressions": []})
            self.assertFalse(loop.attempt("fix bug", "broken").accepted)

    def test_rejects_any_matrix_regression(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self.make_loop(td, "fixed", {"added": True},
                                  {"ok": True, "complete": True, "regressions": ["fixture-7"]})
            result = loop.attempt("fix bug", "broken")
            self.assertFalse(result.accepted)
            self.assertFalse(result.differential_ok)

    def test_rejects_incomplete_matrix(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self.make_loop(td, "fixed", {"added": True}, {"ok": True, "regressions": []})
            self.assertFalse(loop.attempt("fix", "old").accepted)

    def test_dry_run_never_accepts_and_logs_attempt(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self.make_loop(td, "fixed", {"added": True},
                                  {"ok": True, "complete": True, "regressions": []})
            result = loop.attempt("fix bug", "broken", dry_run=True)
            self.assertFalse(result.accepted)
            record = json.loads((Path(td) / "attempts.jsonl").read_text().strip())
            self.assertEqual(record["reason"], "dry-run: all gates passed; no source accepted or written")

    def test_compile_failure_is_logged_and_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            def broken_compile(source):
                raise ValueError("syntax error")
            loop = self.make_loop(td, "bad", {"added": True},
                                  {"ok": True, "complete": True, "regressions": []},
                                  compiler=broken_compile)
            result = loop.attempt("fix", "old")
            self.assertFalse(result.accepted)
            self.assertIn("syntax error", result.diagnostics)
            self.assertTrue((Path(td) / "attempts.jsonl").exists())

    def test_unchanged_proposal_is_rejected_and_logged(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self.make_loop(td, "same", {"added": True},
                                  {"ok": True, "complete": True, "regressions": []})
            result = loop.attempt("fix", "same")
            self.assertFalse(result.accepted)
            self.assertEqual(result.reason, "proposal unchanged")

    def test_adapter_exception_is_logged(self):
        class BrokenAdapter:
            def propose(self, *args):
                raise RuntimeError("provider offline")
        with tempfile.TemporaryDirectory() as td:
            loop = RepairLoop(BrokenAdapter(), compiler=lambda s: None,
                              fixture_runner=lambda s, f: {},
                              differential_runner=lambda s: {},
                              log_path=Path(td) / "attempts.jsonl")
            result = loop.attempt("fix", "old")
            self.assertFalse(result.accepted)
            self.assertIn("provider offline", result.diagnostics)
            self.assertTrue((Path(td) / "attempts.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
