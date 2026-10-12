"""Ensure registry, importer, backends, and conformance share builtin metadata."""
from __future__ import annotations

import unittest

from compiler import js_backend, python_backend
from compiler.import_python import translate
from library.builtin_contract import (
    BUILTIN_BY_NAME,
    BUILTIN_CONTRACT,
    BUILTIN_NAMES,
    PYTHON_BUILTINS,
    PYTHON_MODULES,
    backend_builtins,
    imported_builtin,
    imported_constant,
)
from library.stdlib import BUILTINS, call_builtin


class BuiltinContractTests(unittest.TestCase):
    def test_contract_has_unique_names_and_explicit_target_statuses(self):
        entries = BUILTIN_CONTRACT["builtins"]
        names = [entry["name"] for entry in entries]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), set(BUILTINS))
        self.assertEqual(set(names), set(BUILTIN_NAMES))
        expected_targets = set(BUILTIN_CONTRACT["targets"])
        for entry in entries:
            self.assertEqual(set(entry["backends"]), expected_targets, entry["name"])
            for target, detail in entry["backends"].items():
                self.assertIn(detail["status"], {"supported", "unsupported", "not-claimed"}, (entry["name"], target))

    def test_platform_capabilities_are_explicit_and_not_overclaimed(self):
        capabilities = BUILTIN_CONTRACT["capabilities"]
        ids = [item["id"] for item in capabilities]
        self.assertEqual(len(ids), len(set(ids)))
        by_id = {item["id"]: item for item in capabilities}
        for capability_id in ("data.database", "server.http", "web.dom", "web3.blockchain", "backend.ffi"):
            self.assertEqual(by_id[capability_id]["status"], "planned")
            self.assertEqual(by_id[capability_id]["targets"], [])
        self.assertEqual(by_id["net.http"]["status"], "available")
        self.assertEqual(by_id["net.http"]["targets"], ["python"])
        self.assertFalse(by_id["net.http"]["offline_first"])
        self.assertTrue(by_id["core.pure"]["offline_first"])
        self.assertTrue(by_id["data.database"]["offline_first"])
        self.assertFalse(by_id["net.http"]["offline_first"])

    def test_reference_registry_metadata_is_derived_from_contract(self):
        for name, spec in BUILTIN_BY_NAME.items():
            runtime = BUILTINS[name]
            self.assertEqual(runtime.parameters, tuple(spec["parameters"]), name)
            self.assertEqual(runtime.description, spec["description"], name)
            self.assertEqual(runtime.min_args, spec["min_args"], name)
            self.assertEqual(runtime.max_args, spec["max_args"], name)
        self.assertEqual(call_builtin("rata_rata", [1, 2, 6]), 3)
        self.assertEqual(call_builtin("median", [1, 2, 3, 4]), 2.5)
        with self.assertRaisesRegex(TypeError, "argumen"):
            call_builtin("median")
        with self.assertRaisesRegex(TypeError, "argumen"):
            call_builtin("rentang", 1, 2, 3, 4)

    def test_python_import_allowlist_resolves_only_contract_entries(self):
        for source_name, target_name in PYTHON_BUILTINS.items():
            self.assertIn(target_name, BUILTIN_BY_NAME, source_name)
        for module, spec in PYTHON_MODULES.items():
            for source_name, target_name in spec.get("functions", {}).items():
                self.assertEqual(imported_builtin(module, source_name), target_name)
                self.assertIn(target_name, BUILTIN_BY_NAME)
            for source_name, literal in spec.get("constants", {}).items():
                self.assertEqual(imported_constant(module, source_name), literal)
        translated = translate(
            "import statistics as stats\n"
            "from statistics import mean as average\n"
            "print(stats.mean([1, 2, 6]))\n"
            "print(average([2, 4]))\n"
        )
        self.assertIn("rata_rata([1, 2, 6])", translated)
        self.assertIn("rata_rata([2, 4])", translated)

    def test_backend_dispatch_and_helpers_match_contract(self):
        js_source = __import__("inspect").getsource(js_backend)
        python_source = __import__("inspect").getsource(python_backend)
        for target, mapping, source in (
            ("js", backend_builtins("js"), js_source),
            ("python", backend_builtins("python"), python_source),
        ):
            expected = {
                entry["name"]
                for entry in BUILTIN_CONTRACT["builtins"]
                if entry["backends"][target]["status"] == "supported"
                and "helper" in entry["backends"][target]
            }
            self.assertEqual(set(mapping), expected, target)
            for name, spec in mapping.items():
                helper = spec["helper"]
                self.assertIn(helper, source, f"{target}: {name} -> {helper}")

    def test_importer_rejects_apis_outside_contract(self):
        with self.assertRaisesRegex(ValueError, "statistics.variance"):
            translate("import statistics\nprint(statistics.variance([1, 2, 3]))\n")
        with self.assertRaises(ValueError):
            translate("import requests\n")


if __name__ == "__main__":
    unittest.main()
