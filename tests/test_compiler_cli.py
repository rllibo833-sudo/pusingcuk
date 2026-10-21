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
        self.assertIn("pc_out(pc_num((pc_v_x) - (2.0)));", result)

    def test_rust_target_rejects_unsupported_constructs(self):
        with self.assertRaisesRegex(ValueError, "backend Rust subset"):
            compile_source("jancuk\nmumet benar\n    hedeh 1\nselesai mumet\nselesai jancuk", "demo.cuk", "rust")

    def test_unknown_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "target tidak dikenal"):
            compile_source(SOURCE, "demo.pusingcuk", "wasm")


if __name__ == "__main__":
    unittest.main()
