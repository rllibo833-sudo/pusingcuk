import unittest

from compiler.bootstrap import BootstrapError, build
from compiler.self_hosted_frontend import from_source as self_hosted_from_source


class BootstrapEvidenceTests(unittest.TestCase):

    def test_cuk_frontend_emits_function_and_return_ir_without_fallback(self):
        source = 'jancuk\nfungsi tambah(a, b)\n    balek a + b\nselesai fungsi\nhedeh tambah(20, 22)\nselesai jancuk\n'
        document = self_hosted_from_source(source, "function.cuk")
        body = document["program"]["fields"]["body"]
        self.assertEqual(body[0]["kind"], "Function")
        self.assertEqual(body[0]["fields"]["params"], ["a", "b"])
        self.assertEqual(body[0]["fields"]["body"][0]["kind"], "Return")
        self.assertIn("functions", document["features"])
        self.assertEqual(body[1]["kind"], "Print")
    def test_cuk_frontend_parses_conditional_inside_function_without_python_fallback(self):
        source = 'jancuk\nfungsi pilih(a)\n    njir a > 0\n        balek 1\n    kampret\n        balek 0\n    selesai njir\nselesai fungsi\nhedeh pilih(1)\nselesai jancuk\n'
        document = self_hosted_from_source(source, "conditional-function.cuk")
        function = document["program"]["fields"]["body"][0]
        self.assertEqual(function["kind"], "Function")
        conditional = function["fields"]["body"][0]
        self.assertEqual(conditional["kind"], "If")
        self.assertEqual(conditional["fields"]["then_body"][0]["kind"], "Return")
        self.assertEqual(conditional["fields"]["else_body"][0]["kind"], "Return")
        evidence = build(source, "conditional-function.cuk")
        self.assertEqual(evidence["stages"][0]["stdout"], "1\n")

    def test_two_stage_build_emits_identical_artifacts(self):
        source = 'jancuk\nlah nama = "Dunia"\nhedeh "Halo, " + nama\nselesai jancuk\n'
        evidence = build(source, "hello.cuk")
        self.assertEqual(evidence["schema"], "pusingcuk-bootstrap-evidence")
        self.assertEqual(evidence["status"], "reproducible-subset")
        self.assertFalse(evidence["full_self_hosting"])
        self.assertEqual(evidence["comparison"], "identical")
        self.assertEqual(evidence["stages"][0]["ir_sha256"], evidence["stages"][1]["ir_sha256"])
        self.assertEqual(evidence["stages"][0]["bytecode_sha256"], evidence["stages"][1]["bytecode_sha256"])
        self.assertEqual(evidence["stages"][0]["stdout"], "Halo, Dunia\n")

    def test_bootstrap_compiles_function_program_through_ir_and_vm(self):
        source = 'jancuk\nfungsi tambah(a, b)\n    balek a + b\nselesai fungsi\nhedeh tambah(20, 22)\nselesai jancuk\n'
        evidence = build(source, "function.cuk")
        self.assertEqual(evidence["status"], "reproducible-subset")
        self.assertEqual(evidence["stages"][0]["stdout"], "42\n")
        self.assertEqual(evidence["stages"][0]["bytecode_sha256"], evidence["stages"][1]["bytecode_sha256"])


if __name__ == "__main__":
    unittest.main()
