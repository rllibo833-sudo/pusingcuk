import tempfile
import time
import unittest
from pathlib import Path

from compiler.sandbox import (
    CapabilityDenied, CapabilityPolicy, ResourceBudget, ResourceLimitExceeded,
    parse_permission,
)


class CapabilityPolicyTests(unittest.TestCase):
    def test_default_deny_for_all_host_capabilities(self):
        policy = CapabilityPolicy(cwd="/tmp")
        for capability, target in (
            ("baca", "data/file.txt"), ("tulis", "output/file.txt"),
            ("jaringan", "api.example"), ("proses", "tool"), ("env", "HOME"),
        ):
            with self.subTest(capability=capability):
                with self.assertRaises(CapabilityDenied):
                    policy.require(capability, target)

    def test_granted_file_root_allows_descendant_and_denies_escape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "data").mkdir()
            policy = CapabilityPolicy(["baca:./data"], cwd=root)
            self.assertEqual(policy.resolve_file("baca", "data/file.txt"), root / "data" / "file.txt")
            with self.assertRaises(CapabilityDenied):
                policy.require("baca", "../secret.txt")

    def test_symlink_escape_is_denied(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            root = Path(td)
            (root / "data").mkdir()
            (root / "data" / "escape").symlink_to(outside, target_is_directory=True)
            policy = CapabilityPolicy(["baca:./data"], cwd=root)
            with self.assertRaises(CapabilityDenied):
                policy.require("baca", "data/escape/secret.txt")

    def test_named_capabilities_require_exact_target(self):
        policy = CapabilityPolicy(["jaringan:api.example", "proses:reporter", "env:LANG"])
        policy.require("jaringan", "api.example")
        policy.require("proses", "reporter")
        policy.require("env", "LANG")
        for capability, target in (("jaringan", "evil.example"), ("proses", "shell"), ("env", "HOME")):
            with self.subTest(capability=capability):
                with self.assertRaises(CapabilityDenied):
                    policy.require(capability, target)

    def test_bad_permissions_rejected(self):
        for spec in ("", "root:/", "env", "baca", "proses:"):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    parse_permission(spec)

    def test_fuel_memory_and_time_limits(self):
        budget = ResourceBudget(fuel=1, memory_bytes=100_000, time_seconds=1)
        budget.tick("small")
        with self.assertRaises(ResourceLimitExceeded):
            budget.tick("small")

        memory_budget = ResourceBudget(fuel=10, memory_bytes=1, time_seconds=1)
        with self.assertRaises(ResourceLimitExceeded):
            memory_budget.tick("object larger than one byte")

        time_budget = ResourceBudget(fuel=10, memory_bytes=100_000, time_seconds=0.001)
        time.sleep(0.01)
        with self.assertRaises(ResourceLimitExceeded):
            time_budget.tick("small")


if __name__ == "__main__":
    unittest.main()
