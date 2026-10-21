"""Execute output from the .cuk-authored frontend through IR v1 and the bytecode VM."""
from __future__ import annotations

import io
import unittest

from compiler.bytecode import compile_ir
from compiler.self_hosted_frontend import from_source
from compiler.vm import VirtualMachine


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


if __name__ == "__main__":
    unittest.main()
