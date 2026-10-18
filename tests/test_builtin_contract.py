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
        self.assertEqual(by_id["net.http"]["targets"], ["reference"])
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
        self.assertEqual(call_builtin("jumlah", []), 0)
        self.assertEqual(call_builtin("jumlah", [1, 2, 6]), 9)
        self.assertEqual(call_builtin("jumlah", [-8, 3, 5]), 0)
        self.assertEqual(call_builtin("jumlah", [9007199254740991, 0]), 9007199254740991)
        self.assertEqual(call_builtin("jumlah", [-9007199254740991, 9007199254740991]), 0)
        self.assertEqual(call_builtin("jumlah", [0.1, 0.2, 0.3]), 0.6000000000000001)
        with self.assertRaises(TypeError):
            call_builtin("jumlah", [1, True])
        with self.assertRaises(TypeError):
            call_builtin("jumlah", [1, float("nan")])
        with self.assertRaises(ValueError):
            call_builtin("jumlah", [9007199254740992])
        with self.assertRaises(ValueError):
            call_builtin("jumlah", [9007199254740991, 1])
        with self.assertRaises(ValueError):
            call_builtin("jumlah", [9007199254740991, 1, -1])
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
            "print(sum([1, 2, 6]))\n"
        )
        self.assertIn("rata_rata([1, 2, 6])", translated)
        self.assertIn("rata_rata([2, 4])", translated)
        self.assertIn("jumlah([1, 2, 6])", translated)

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



    def test_all_reference_builtins_execute_with_language_semantics(self):
        examples = {
            "panjang": (("cuk",), 3),
            "teks": ((True,), "okelah"),
            "bilangan": (("42",), 42),
            "desimal": (("1.5",), 1.5),
            "logika": ((0,), False),
            "rentang": ((1, 4), [1, 2, 3]),
            "mutlak": ((-2,), 2),
            "minimum": ((2, 5), 2),
            "maksimum": ((2, 5), 5),
            "bulatkan": ((2.5,), 2),
            "akar": ((9,), 3),
            "bawah": ((2.9,), 2),
            "atas": ((2.1,), 3),
            "pangkat": ((2, 3), 8),
            "logaritma": ((2.718281828459045,), 1),
            "log10": ((100,), 2),
            "sinus": ((0,), 0.0),
            "kosinus": ((0,), 1.0),
            "rata_rata": (([1, 2, 3],), 2),
            "median": (([1, 2, 3, 4],), 2.5),
            "jumlah": (([1, 2, 6],), 9),
            "json_teks": (({"nama": "Budi", "aktif": True},), '{"nama":"Budi","aktif":true}'),
            "json_baca": (('{"nama":"Budi","aktif":true}',), {"nama": "Budi", "aktif": True}),
            "html_aman": (("<b>&\"'",), "&lt;b&gt;&amp;&quot;&#x27;"),
            "csv_baris": ((["Budi", "kopi, susu", 'dia bilang "hai"'],), 'Budi,"kopi, susu","dia bilang ""hai"""'),
        }
        self.assertEqual(set(examples), set(BUILTIN_NAMES))
        for name, (args, expected) in examples.items():
            with self.subTest(builtin=name):
                self.assertEqual(call_builtin(name, *args), expected)
                with self.assertRaises(TypeError):
                    call_builtin(name)
                with self.assertRaises(TypeError):
                    call_builtin(name, *args, None)


    def test_length_builtin_covers_all_documented_collection_shapes(self):
        self.assertEqual(call_builtin("panjang", "PusingCuk"), 9)
        self.assertEqual(call_builtin("panjang", [1, 2, 3]), 3)
        self.assertEqual(call_builtin("panjang", {"kopi": 1, "teh": 2}), 2)
        self.assertEqual(call_builtin("panjang", call_builtin("rentang", 2, 5)), 3)
        with self.assertRaises((TypeError, ValueError)):
            call_builtin("panjang", 42)

    def test_minimum_maximum_and_rounding_boundary_contract(self):
        self.assertEqual(call_builtin("minimum", -9, 0), -9)
        self.assertEqual(call_builtin("minimum", 0, 0), 0)
        self.assertEqual(call_builtin("maksimum", -9, 0), 0)
        self.assertEqual(call_builtin("maksimum", -9, -2), -2)
        self.assertEqual(call_builtin("bulatkan", 2.5), 2)
        self.assertEqual(call_builtin("bulatkan", 3.5), 4)
        self.assertEqual(call_builtin("bulatkan", -2.5), -2)
        with self.assertRaises(TypeError):
            call_builtin("minimum", True, 1)
        with self.assertRaises(TypeError):
            call_builtin("maksimum", 1, False)

    def test_decimal_conversion_rejects_non_finite_values(self):
        for invalid in ("nan", "inf", "-inf", float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=invalid):
                with self.assertRaises((TypeError, ValueError)):
                    call_builtin("desimal", invalid)

    def test_square_root_and_power_numeric_contract(self):
        self.assertIs(type(call_builtin("akar", 9)), int)
        self.assertIs(type(call_builtin("pangkat", 2, 3)), int)
        self.assertEqual(call_builtin("pangkat", 2, -1), 0.5)
        self.assertAlmostEqual(call_builtin("akar", 2), 2 ** 0.5)
        self.assertAlmostEqual(call_builtin("pangkat", 2, 0.5), 2 ** 0.5)
        with self.assertRaises(TypeError):
            call_builtin("akar", True)
        with self.assertRaises(TypeError):
            call_builtin("pangkat", 2, False)
        for name, args in (
            ("akar", (-1,)),
            ("pangkat", (-2, 0.5)),
            ("pangkat", (0, -1)),
            ("pangkat", (10, 1000)),
        ):
            with self.subTest(builtin=name, args=args):
                with self.assertRaises(ValueError):
                    call_builtin(name, *args)

    def test_trigonometry_and_statistics_numeric_contract(self):
        self.assertIs(type(call_builtin("sinus", 0)), int)
        self.assertIs(type(call_builtin("kosinus", 0)), int)
        self.assertEqual(call_builtin("sinus", 0), 0)
        self.assertEqual(call_builtin("kosinus", 0), 1)
        self.assertAlmostEqual(call_builtin("sinus", 0.5), 0.479425538604203)
        self.assertAlmostEqual(call_builtin("kosinus", 0.5), 0.8775825618903728)
        self.assertEqual(call_builtin("rata_rata", [1, 2, 6]), 3)
        self.assertEqual(call_builtin("rata_rata", [-2, 1]), -0.5)
        self.assertEqual(call_builtin("median", [1, 2, 9]), 2)
        self.assertEqual(call_builtin("median", [1, 4, 8, 9]), 6)
        self.assertEqual(call_builtin("median", [-3, -1, 4, 8]), 1.5)
        self.assertEqual(call_builtin("rata_rata", [9007199254740991]), 9007199254740991)
        self.assertEqual(call_builtin("rata_rata", [-9007199254740991, 9007199254740991]), 0)
        self.assertEqual(call_builtin("rata_rata", [0.1, 0.2, 0.3]), 0.2)
        self.assertEqual(call_builtin("median", [9007199254740991, 9007199254740991]), 9007199254740991)
        self.assertEqual(call_builtin("median", [-9007199254740991, 9007199254740991]), 0)
        self.assertEqual(call_builtin("median", [5, 5, 5, 5]), 5)
        self.assertEqual(call_builtin("median", [-0.5, 0.5]), 0)

        for name in ("sinus", "kosinus"):
            with self.subTest(builtin=name):
                for invalid in (True, "0", float("inf")):
                    with self.assertRaises(TypeError):
                        call_builtin(name, invalid)
        for name in ("rata_rata", "median"):
            with self.subTest(builtin=name):
                for invalid in ([], [1, True], [1, "2"], [1, float("inf")]):
                    with self.assertRaises(TypeError):
                        call_builtin(name, invalid)
                with self.assertRaises(ValueError):
                    call_builtin(name, [9007199254740992])
        for name, args in (
            ("sinus", ()), ("sinus", (0, 1)),
            ("kosinus", ()), ("kosinus", (0, 1)),
            ("rata_rata", ()), ("rata_rata", ([1], [2])),
            ("median", ()), ("median", ([1], [2])),
        ):
            with self.subTest(builtin=name, args=args):
                with self.assertRaises(TypeError):
                    call_builtin(name, *args)

    def test_logarithmic_numeric_contract(self):
        self.assertEqual(call_builtin("logaritma", 1), 0)
        self.assertEqual(call_builtin("logaritma", 2.718281828459045), 1)
        self.assertEqual(call_builtin("log10", 100), 2)
        for name in ("logaritma", "log10"):
            with self.subTest(builtin=name):
                for invalid in (0, -1, True, "2", float("inf")):
                    with self.assertRaises((TypeError, ValueError)):
                        call_builtin(name, invalid)
                with self.assertRaises(TypeError):
                    call_builtin(name)
                with self.assertRaises(TypeError):
                    call_builtin(name, 1, 2)

    def test_native_c_support_status_matches_implemented_builtin_surface(self):
        native_supported = {
            "panjang", "rentang", "mutlak", "minimum", "maksimum", "bulatkan",
            "bawah", "atas", "akar", "pangkat", "logaritma", "log10", "sinus", "kosinus", "jumlah", "rata_rata", "median",
        }
        native_partial = {"teks", "bilangan", "desimal", "logika"}
        for name, entry in BUILTIN_BY_NAME.items():
            with self.subTest(builtin=name):
                if name in native_supported:
                    expected = "supported"
                elif name in native_partial:
                    expected = "not-claimed"
                else:
                    expected = "unsupported"
                self.assertEqual(entry["backends"]["native_c"]["status"], expected)

    def test_human_builtin_catalog_matches_canonical_contract(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        doc = (root / "docs" / "language" / "BUILTINS.md").read_text(encoding="utf-8")
        rows = [line for line in doc.splitlines() if line.startswith("| `")]
        parsed = {}
        targets = ("reference", "native_c", "js", "python", "html", "vm")
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if len(cells) != 9:
                continue
            name = cells[0].strip("`")
            parsed[name] = {
                "arity": cells[1],
                "description": cells[2],
                "statuses": dict(zip(targets, cells[3:9])),
            }
        self.assertEqual(set(parsed), set(BUILTIN_BY_NAME))
        for name, entry in BUILTIN_BY_NAME.items():
            with self.subTest(builtin=name):
                arity = str(entry["min_args"]) if entry["min_args"] == entry["max_args"] else f'{entry["min_args"]}–{entry["max_args"]}'
                self.assertEqual(parsed[name]["arity"], arity)
                self.assertEqual(parsed[name]["description"], entry["description"])
                self.assertEqual(
                    parsed[name]["statuses"],
                    {target: entry["backends"][target]["status"] for target in targets},
                )

if __name__ == "__main__":
    unittest.main()
