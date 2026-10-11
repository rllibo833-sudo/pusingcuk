import json
import unittest

from compiler import compile_source


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

    def test_python_target_emits_python_source(self):
        result = compile_source(SOURCE, "demo.pusingcuk", "python")
        compile(result, "demo.py", "exec")
        self.assertIn("pc_out(42)", result)

    def test_html_target_contains_inline_javascript_and_output_panel(self):
        result = compile_source(SOURCE, "demo.pusingcuk", "html")
        self.assertIn('<pre id="pc-output">', result)
        self.assertIn("pcOut(42)", result)
        self.assertIn("</html>", result)

    def test_unknown_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "target tidak dikenal"):
            compile_source(SOURCE, "demo.pusingcuk", "wasm")


if __name__ == "__main__":
    unittest.main()
