import math
import unittest

from compiler.ir import (
    FORMAT, IR_VERSION, IRValidationError, dumps, from_source, loads, validate,
)

SOURCE = """jancuk
lah nilai = 6 * 7
hedeh nilai
selesai jancuk
"""


class IRTests(unittest.TestCase):
    def test_round_trip_is_deterministic(self):
        document = from_source(SOURCE, "contoh.pusingcuk")
        encoded = dumps(document)
        self.assertEqual(loads(encoded), document)
        self.assertEqual(dumps(loads(encoded)), encoded)
        self.assertEqual(document["format"], FORMAT)
        self.assertEqual(document["ir_version"], IR_VERSION)
        self.assertEqual(document["source_name"], "contoh.pusingcuk")

    def test_features_are_derived_from_ast(self):
        document = from_source(
            "jancuk\nfungsi tambah(a, b)\nbalek a + b\nselesai fungsi\n"
            "hedeh tambah(1, 2)\nselesai jancuk"
        )
        self.assertIn("functions", document["features"])
        self.assertIn("calls", document["features"])
        self.assertIn("operators", document["features"])

    def test_source_map_records_node_lines(self):
        document = from_source(SOURCE)
        self.assertTrue(document["source_map"])
        self.assertEqual(document["source_map"][0]["path"], "$")
        self.assertTrue(all(item["line"] >= 1 for item in document["source_map"]))

    def test_rejects_unknown_version(self):
        document = from_source(SOURCE)
        document["ir_version"] = 2
        with self.assertRaisesRegex(IRValidationError, "versi IR"):
            validate(document)

    def test_rejects_unknown_node(self):
        document = from_source(SOURCE)
        document["program"]["kind"] = "ExecuteShell"
        with self.assertRaisesRegex(IRValidationError, "jenis node"):
            validate(document)

    def test_rejects_nonfinite_numbers(self):
        document = from_source(SOURCE)
        document["program"]["fields"]["body"][0]["fields"]["value"]["fields"]["left"]["fields"]["value"] = math.inf
        with self.assertRaisesRegex(IRValidationError, "non-finite"):
            validate(document)

    def test_rejects_duplicate_or_unsorted_features(self):
        document = from_source(SOURCE)
        document["features"].append("core")
        with self.assertRaisesRegex(IRValidationError, "unik dan terurut"):
            validate(document)

    def test_rejects_unknown_envelope_fields(self):
        document = from_source(SOURCE)
        document["backend_hint"] = "c"
        with self.assertRaisesRegex(IRValidationError, "envelope"):
            validate(document)

    def test_rejects_malformed_json(self):
        with self.assertRaises(IRValidationError):
            loads('{"ir_version": NaN}')

    def test_source_name_is_not_an_absolute_path(self):
        document = from_source(SOURCE, "/tmp/private/project.pusingcuk")
        self.assertEqual(document["source_name"], "project.pusingcuk")


if __name__ == "__main__":
    unittest.main()
