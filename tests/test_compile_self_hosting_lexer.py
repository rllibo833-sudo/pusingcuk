"""Regression: top-level functions in the self-hosting lexer compile to PVM."""
from pathlib import Path
import unittest

from compiler.bytecode import compile_source


class CompileSelfHostingLexerTests(unittest.TestCase):
    def test_source_lexer_compiles_with_top_level_functions(self):
        source_path = Path(__file__).resolve().parents[1] / "examples" / "self_hosting" / "source_lexer.cuk"
        artifact = compile_source(source_path.read_text(encoding="utf-8"), source_path.name)

        self.assertEqual(artifact["format"], "pusingcuk-bytecode")
        self.assertEqual(artifact["bytecode_version"], 1)
        self.assertGreater(len(artifact["functions"]), 0)
        self.assertIn("pindai", artifact["functions"])
        self.assertIn("parse_source", artifact["functions"])


if __name__ == "__main__":
    unittest.main()
