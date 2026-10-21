import json
import unittest

from compiler.__main__ import compile_source


SOURCE = "jancuk\nhedeh 42\nselesai jancuk"


class MultiTargetCompilerTests(unittest.TestCase):
    def test_json_target_emits_valid_ir(self):
        result = compile_source(SOURCE, "demo.pusingcuk", "json")
        document = json.loads(result)
        self.assertEqual(document["format"], "pusingcuk-ir")
        self.assertEqual(document["ir_version"], 1)

    def test_javascript_target_emits_executable_source(self):
        result = compile_source(SOURCE, "demo.pusingcuk", "js")
        self.assertIn("PusingCuk JavaScript backend runtime", result)
        self.assertIn("pcOut(42)", result)

    def test_c_target_emits_standalone_c_source(self):
        result = compile_source(SOURCE, "demo.cuk", "c")
        self.assertIn("#include <inttypes.h>", result)
        self.assertIn("int main(void)", result)
        self.assertIn("pc_out", result) if "pc_out" in result else self.assertIn("printf", result)

    def test_python_target_emits_python_source(self):
        result = compile_source(SOURCE, "demo.pusingcuk", "python")
        compile(result, "demo.py", "exec")
        self.assertIn("pc_out(42)", result)

    def test_html_target_contains_inline_javascript_and_output_panel(self):
        result = compile_source(SOURCE, "demo.pusingcuk", "html")
        self.assertIn('<pre id="pc-output">', result)
        self.assertIn("pcOut(42)", result)
        self.assertIn("</html>", result)

    def test_numeric_standard_library_is_lowered_in_js_and_python(self):
        source = "jancuk\nhedeh mutlak(-8)\nhedeh minimum(4, 9)\nhedeh maksimum(4, 9)\nhedeh bulatkan(2.5)\nselesai jancuk"
        js = compile_source(source, "builtins.pusingcuk", "js")
        self.assertIn("pcAbs(pcNeg(8))", js)
        self.assertIn("pcMin(4, 9)", js)
        self.assertIn("pcMax(4, 9)", js)
        self.assertIn("pcRound(2.5)", js)
        py = compile_source(source, "builtins.pusingcuk", "python")
        compile(py, "builtins.py", "exec")
        self.assertIn("pc_abs((-(8)))", py)
        self.assertIn("pc_min(4, 9)", py)
        self.assertIn("pc_max(4, 9)", py)
        self.assertIn("pc_round(2.5)", py)

    def test_go_target_emits_standalone_source(self):
        result = compile_source(SOURCE, "demo.cuk", "go")
        self.assertIn("package main", result)
        self.assertIn("func main()", result)
        self.assertIn("pcOut(pcLiteral(float64(42), 2))", result)

    def test_cpp_target_emits_standalone_cpp17_source(self):
        result = compile_source(SOURCE, "demo.cuk", "cpp")
        self.assertIn("#include <variant>", result)
        self.assertIn("int main()", result)
        self.assertIn("pcOut(Value(pcSafe", result)

    def test_rust_target_emits_standalone_numeric_program(self):
        result = compile_source(
            "jancuk\nlah x = 7 + 5 * 6\nx = x - 2\nhedeh x\nselesai jancuk",
            "demo.cuk", "rust",
        )
        self.assertIn("fn main()", result)
        self.assertIn("pc_num((7.0) + (pc_num((5.0) * (6.0))))", result)
        self.assertIn("pc_v_x = pc_num((pc_v_x) - (2.0));", result)

    def test_self_hosted_frontend_emits_canonical_ir_and_uses_existing_backend(self):
        from compiler.self_hosted_frontend import from_source as selfhost_from_source
        source = "jancuk\nlah x = 7 + 5 * 6\nx = x - 2\nhedeh x\nselesai jancuk"
        canonical = json.loads(compile_source(source, "same.cuk", "json"))
        selfhost_ir = selfhost_from_source(source, "same.cuk")
        self.assertEqual(selfhost_ir["format"], canonical["format"])
        self.assertEqual(selfhost_ir["ir_version"], canonical["ir_version"])
        self.assertEqual(selfhost_ir["program"], canonical["program"])
        generated = compile_source(source, "same.cuk", "js", frontend="selfhosted")
        self.assertIn("pcOut", generated)

    def test_self_hosted_frontend_preserves_string_literals_in_canonical_ir(self):
        from compiler.self_hosted_frontend import from_source as selfhost_from_source
        source = 'jancuk\nlah message = "hello\\n\\"world\\""\nhedeh message\nselesai jancuk'
        canonical = json.loads(compile_source(source, "strings.cuk", "json"))
        selfhost_ir = selfhost_from_source(source, "strings.cuk")
        self.assertEqual(selfhost_ir["program"], canonical["program"])
        self.assertEqual(selfhost_ir["program"]["fields"]["body"][0]["fields"]["value"]["fields"]["value"], 'hello\n"world"')

    def test_self_hosted_frontend_matches_canonical_print_aliases(self):
        from compiler.self_hosted_frontend import from_source as selfhost_from_source
        aliases = ("bacot", "bacrit", "berak", "berisik", "cetak", "crot",
                   "gebber", "gembor", "jedor", "jir", "keluarin", "koar", "muncrat",
                   "ngegas", "nyalak", "omong", "print", "sembur", "semprot", "senggol",
                   "spill", "suarakan", "tampilkan", "teriak")
        source = "jancuk\nlah x = 9\n" + "\n".join(f"{alias} x" for alias in aliases) + "\nselesai jancuk"
        canonical = json.loads(compile_source(source, "aliases.cuk", "json"))
        selfhost_ir = selfhost_from_source(source, "aliases.cuk")
        self.assertEqual(selfhost_ir["program"], canonical["program"])
        generated = compile_source(source, "aliases.cuk", "js", frontend="selfhosted")
        self.assertEqual(generated.count("pcOut("), len(aliases))

    def test_self_hosted_frontend_supports_decimal_literals(self):
        from compiler.self_hosted_frontend import from_source as selfhost_from_source
        source = "jancuk\nlah pi = 3.125\nhedeh pi\nselesai jancuk"
        canonical = json.loads(compile_source(source, "decimal.cuk", "json"))
        selfhost_ir = selfhost_from_source(source, "decimal.cuk")
        self.assertEqual(selfhost_ir["program"], canonical["program"])
        self.assertEqual(
            selfhost_ir["program"]["fields"]["body"][0]["fields"]["value"]["fields"]["value"],
            3.125,
        )

    def test_self_hosted_frontend_supports_boolean_literals(self):
        from compiler.self_hosted_frontend import from_source as selfhost_from_source
        source = "jancuk\nlah aktif = benar\nlah nonaktif = salah\nhedeh aktif\nselesai jancuk"
        canonical = json.loads(compile_source(source, "boolean.cuk", "json"))
        selfhost_ir = selfhost_from_source(source, "boolean.cuk")
        self.assertEqual(selfhost_ir["program"], canonical["program"])
        values = [
            item["fields"]["value"]["fields"]["value"]
            for item in selfhost_ir["program"]["fields"]["body"][:2]
        ]
        self.assertEqual(values, [True, False])

    def test_self_hosted_frontend_emits_its_own_ir_envelope(self):
        from compiler.self_hosted_frontend import from_source as selfhost_from_source
        source = "jancuk\nlah x = 2 + 3\nhedeh x\nselesai jancuk"
        canonical = json.loads(compile_source(source, "envelope.cuk", "json"))
        emitted = selfhost_from_source(source, "envelope.cuk")
        self.assertEqual(emitted["format"], canonical["format"])
        self.assertEqual(emitted["ir_version"], canonical["ir_version"])
        self.assertEqual(emitted["language_version"], canonical["language_version"])
        self.assertEqual(emitted["source_name"], canonical["source_name"])
        self.assertEqual(emitted["features"], canonical["features"])
        self.assertEqual(emitted["source_map"], canonical["source_map"])
        self.assertEqual(emitted["program"], canonical["program"])

    def test_self_hosted_frontend_supports_comparison_logic_and_floor_division(self):
        from compiler.self_hosted_frontend import from_source as selfhost_from_source
        source = "jancuk\nlah pembagian = 17 // 5\nlah cocok = pembagian == 3\nlah aktif = cocok dan bukan salah\nhedeh aktif\nselesai jancuk"
        canonical = json.loads(compile_source(source, "operators.cuk", "json"))
        emitted = selfhost_from_source(source, "operators.cuk")
        self.assertEqual(emitted["program"], canonical["program"])
        self.assertEqual(emitted["features"], canonical["features"])
        self.assertEqual(emitted["source_map"], canonical["source_map"])

    def test_frontend_artifact_executes_in_vm_without_python_parser_at_runtime(self):
        import io
        from compiler.bytecode import compile_ir
        from compiler.ir import from_source as reference_from_source
        from compiler.self_hosted_frontend import _frontend_script, from_source as selfhost_from_source
        from compiler.vm import VirtualMachine

        sample = "jancuk\nlah nilai = (2 + 3) * 4\nhedeh nilai\nselesai jancuk"
        expected = selfhost_from_source(sample, "stage1_probe.cuk")
        script = _frontend_script(sample, "stage1_probe.cuk")
        stage0_ir = reference_from_source(script, "stage0_frontend.cuk")
        stage1_artifact = compile_ir(stage0_ir)
        output = io.StringIO()
        VirtualMachine(stage1_artifact, output_stream=output).run()
        emitted = json.loads(output.getvalue().strip().splitlines()[-1])
        self.assertEqual(emitted, expected)

    def test_self_hosted_frontend_rejects_malformed_program(self):
        from compiler.self_hosted_frontend import SelfHostedFrontendError, from_source as selfhost_from_source
        with self.assertRaises(SelfHostedFrontendError):
            selfhost_from_source("jancuk\nlah = 4\nselesai jancuk", "broken.cuk")

    def test_rust_target_rejects_unsupported_constructs(self):
        with self.assertRaisesRegex(ValueError, "backend Rust subset"):
            compile_source("jancuk\nmumet benar\n    hedeh 1\nselesai mumet\nselesai jancuk", "demo.cuk", "rust")

    def test_unknown_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "target tidak dikenal"):
            compile_source(SOURCE, "demo.pusingcuk", "wasm")


if __name__ == "__main__":
    unittest.main()
