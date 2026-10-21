"""Execute output from the .cuk-authored frontend through IR v1 and the bytecode VM."""
from __future__ import annotations

import io
import unittest
from pathlib import Path

from compiler.bytecode import compile_ir
from compiler.ir import from_source as reference_from_source
from compiler.self_hosted_frontend import from_source
from compiler.vm import VirtualMachine


ROOT = Path(__file__).resolve().parents[1]


def without_locations(value):
    if isinstance(value, dict):
        return {key: without_locations(item) for key, item in value.items() if key != "line"}
    if isinstance(value, list):
        return [without_locations(item) for item in value]
    return value


class CompiledFrontendVMTests(unittest.TestCase):
    def test_compiled_cuk_frontend_executes_in_vm(self) -> None:
        source = "lah nilai = (2 + 3) * 4\nhedeh nilai\n"
        ir = from_source(source, "frontend_vm_probe.cuk")
        self.assertEqual(ir["format"], "pusingcuk-ir")
        self.assertEqual(ir["ir_version"], 1)

        bytecode = compile_ir(ir)
        output = io.StringIO()
        VirtualMachine(bytecode, output_stream=output).run()

        self.assertEqual(output.getvalue(), "20\n")

    def test_frontend_parses_its_own_source_without_reference_fallback(self) -> None:
        source = (ROOT / "examples" / "self_hosting" / "compiler.cuk").read_text(encoding="utf-8")
        actual = from_source(source, "compiler.cuk")
        canonical = reference_from_source(source, "compiler.cuk")
        self.assertEqual(
            without_locations(actual["program"]),
            without_locations(canonical["program"]),
        )
        for feature in (
            "calls", "control-flow", "dictionaries", "functions", "indexing",
            "lists", "operators", "variables",
        ):
            self.assertIn(feature, actual["features"])

    def test_frontend_collections_and_nested_control_flow_reach_vm(self) -> None:
        source = (
            "lah data = [1, 2, 3]\n"
            "data[1] = 7\n"
            "lah mapping = {\"value\": data[1]}\n"
            "lah i = 0\n"
            "mumet i < 2\n"
            "    data[0] = data[0] + 1\n"
            "    i = i + 1\n"
            "selesai mumet\n"
            "njir mapping[\"value\"] == 7\n"
            "    hedeh data[0]\n"
            "kampret\n"
            "    hedeh 0\n"
            "selesai njir\n"
            "untuk item dalam data\n"
            "    hedeh item\n"
            "selesai untuk\n"
        )
        ir = from_source(source, "collections_control_flow.cuk")
        bytecode = compile_ir(ir)
        output = io.StringIO()
        VirtualMachine(bytecode, output_stream=output).run()
        self.assertEqual(output.getvalue(), "3\n3\n7\n3\n")


if __name__ == "__main__":
    unittest.main()
