"""Trust-boundary regression tests for registered .cuk rule evidence."""
from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from library.ai_tools import (
    ToolRegistry,
    _THRESHOLD_SHA256,
    _THRESHOLD_SOURCE_COMMIT,
    _THRESHOLD_RUNTIME_VERSION,
)


class _FakeResponse:
    def __init__(self, payload):
        self.raw = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, size=-1):
        return self.raw if size < 0 else self.raw[:size]


class _FakeOpener:
    def __init__(self, mutate=None):
        self.mutate = mutate
        self.request = None
        self.timeout = None

    def open(self, request, *, timeout):
        self.request = request
        self.timeout = timeout
        sent = json.loads(request.data.decode("utf-8"))
        response = {
            "contract_version": "pusingcuk.core.tool.v1",
            "request_id": sent["request_id"],
            "program_id": "budget.threshold.v1",
            "program_sha256": _THRESHOLD_SHA256,
            "source_commit": _THRESHOLD_SOURCE_COMMIT,
            "runtime_version": _THRESHOLD_RUNTIME_VERSION,
            "runtime_build_sha": _THRESHOLD_SOURCE_COMMIT,
            "sandbox": "docker-isolated",
            "sandbox_image": "sha256:" + "a" * 64,
            "status": "succeeded",
            "result": "DALAM_BATAS",
            "elapsed_ms": 12,
        }
        if self.mutate:
            self.mutate(response, sent)
        return _FakeResponse(response)


class RegisteredRuleEvidenceTests(unittest.TestCase):
    def run_rule(self, mutate=None):
        opener = _FakeOpener(mutate)
        with (
            patch.dict(os.environ, {"PUSINGCUK_RUNNER_TOKEN": "t" * 48}),
            patch("library.ai_tools.build_opener", return_value=opener),
        ):
            result = ToolRegistry._run_registered_threshold({"nominal": 2, "batas": 3})
        return result, opener

    def test_accepts_complete_matching_execution_evidence(self):
        result, opener = self.run_rule()
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["result"], "DALAM_BATAS")
        self.assertEqual(result["source_commit"], _THRESHOLD_SOURCE_COMMIT)
        self.assertEqual(result["runtime_build_sha"], _THRESHOLD_SOURCE_COMMIT)
        self.assertEqual(result["elapsed_ms"], 12)
        self.assertEqual(opener.timeout, 4)
        self.assertEqual(opener.request.get_header("Authorization"), "Bearer " + "t" * 48)

    def test_rejects_wrong_source_commit(self):
        result, _ = self.run_rule(lambda response, _sent: response.update(source_commit="f" * 40))
        self.assertEqual(result, {"ok": False, "error": "RULE_EVIDENCE_INVALID"})

    def test_rejects_wrong_runtime_build(self):
        result, _ = self.run_rule(lambda response, _sent: response.update(runtime_build_sha="f" * 40))
        self.assertEqual(result, {"ok": False, "error": "RULE_EVIDENCE_INVALID"})

    def test_rejects_non_matching_request_id(self):
        result, _ = self.run_rule(lambda response, _sent: response.update(request_id="0" * 36))
        self.assertEqual(result, {"ok": False, "error": "RULE_EVIDENCE_INVALID"})

    def test_rejects_missing_or_non_digest_sandbox_image(self):
        for image in (None, "latest", "sha256:" + "G" * 64):
            with self.subTest(image=image):
                result, _ = self.run_rule(lambda response, _sent: response.update(sandbox_image=image))
                self.assertEqual(result, {"ok": False, "error": "RULE_EVIDENCE_INVALID"})

    def test_rejects_invalid_execution_duration(self):
        for elapsed in (None, True, -1, 3001, "12"):
            with self.subTest(elapsed=elapsed):
                result, _ = self.run_rule(lambda response, _sent: response.update(elapsed_ms=elapsed))
                self.assertEqual(result, {"ok": False, "error": "RULE_EVIDENCE_INVALID"})

    def test_rejects_other_contract_and_runtime_identity(self):
        mutations = (
            lambda response, _sent: response.update(contract_version="unrecognized.v9"),
            lambda response, _sent: response.update(runtime_version="unknown"),
            lambda response, _sent: response.update(sandbox="not-isolated"),
            lambda response, _sent: response.update(program_sha256="0" * 64),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                result, _ = self.run_rule(mutate)
                self.assertEqual(result, {"ok": False, "error": "RULE_EVIDENCE_INVALID"})


if __name__ == "__main__":
    unittest.main()
