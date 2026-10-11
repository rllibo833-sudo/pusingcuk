"""Tests for experimental Pusingcuk AST-IR serialization and validation."""
import copy
import json
import unittest

from compiler_ir import IRValidationError, lower_to_ir, validate_ir


SOURCE = """jancuk
fungsi tambah(a, b)
    balek a + b
selesai fungsi
hedeh tambah(20, 22)
selesai jancuk
"""


class CompilerIRTests(unittest.TestCase):
    def test_lowering_is_deterministic(self):
        first = lower_to_ir(SOURCE, "example.pusingcuk")
        second = lower_to_ir(SOURCE, "example.pusingcuk")
        self.assertEqual(first, second)
        self.assertEqual(
            json.dumps(first, ensure_ascii=False, sort_keys=True),
            json.dumps(second, ensure_ascii=False, sort_keys=True),
        )

    def test_ir_has_version_features_and_source_map(self):
        document = lower_to_ir(SOURCE, "example.pusingcuk")
        self.assertEqual(document["format"], "pusingcuk-ast-ir")
        self.assertEqual(document["ir_version"], 1)
        self.assertIn("Function", document["features"])
        self.assertIn("Binary", document["features"])
        self.assertEqual(document["source_map"][0]["source"], "example.pusingcuk")
        self.assertIs(validate_ir(document), document)

    def test_rejects_unknown_ir_version(self):
        document = lower_to_ir(SOURCE)
        document["ir_version"] = 999
        with self.assertRaisesRegex(IRValidationError, "versi IR"):
            validate_ir(document)

    def test_rejects_duplicate_node_ids(self):
        document = lower_to_ir(SOURCE)
        document["program"]["fields"]["body"][0]["node_id"] = document["program"]["node_id"]
        with self.assertRaisesRegex(IRValidationError, "duplikat"):
            validate_ir(document)

    def test_rejects_unknown_node_kind(self):
        document = lower_to_ir(SOURCE)
        document["program"]["kind"] = "ExecuteHostCode"
        with self.assertRaisesRegex(IRValidationError, "jenis node tidak dikenal"):
            validate_ir(document)

    def test_rejects_source_map_mismatch(self):
        document = lower_to_ir(SOURCE)
        document["source_map"][0]["line"] = 999
        with self.assertRaisesRegex(IRValidationError, "source_map"):
            validate_ir(document)

    def test_rejects_extra_document_fields(self):
        document = lower_to_ir(SOURCE)
        document["backend_command"] = "arbitrary"
        with self.assertRaisesRegex(IRValidationError, "field dokumen"):
            validate_ir(document)

    def test_rejects_non_finite_literal_during_serialization(self):
        with self.assertRaisesRegex(IRValidationError, "non-finite"):
            lower_to_ir("jancuk\nhedeh 1e999\nselesai jancuk\n")


if __name__ == "__main__":
    unittest.main()
