import unittest

from compiler.typesystem import (
    ANY, BOOL, FLOAT, INT, NULL, STRING, TypeKind, common_type, infer_type,
    is_assignable, list_of, map_of, optional_of, result_of, struct_of, enum_of,
)
from library.stdlib import BUILTINS, call_builtin, get_builtin


class TypeSystemTests(unittest.TestCase):
    def test_bool_is_not_inferred_as_integer(self):
        self.assertEqual(infer_type(True), BOOL)
        self.assertEqual(infer_type(3), INT)

    def test_literal_inference(self):
        self.assertEqual(infer_type("hai"), STRING)
        self.assertEqual(infer_type(2.5), FLOAT)
        self.assertEqual(infer_type([1, 2]), list_of(INT))
        self.assertEqual(infer_type([1, "dua"]), list_of(ANY))
        self.assertEqual(infer_type({"a": 1}), map_of(STRING, INT))

    def test_numeric_assignment_is_one_way(self):
        self.assertTrue(is_assignable(FLOAT, INT))
        self.assertFalse(is_assignable(INT, FLOAT))

    def test_nested_collection_assignment(self):
        self.assertTrue(is_assignable(list_of(FLOAT), list_of(INT)))
        self.assertFalse(is_assignable(list_of(INT), list_of(STRING)))

    def test_any_is_permissive(self):
        self.assertTrue(is_assignable(INT, ANY))
        self.assertTrue(is_assignable(ANY, STRING))

    def test_common_type(self):
        self.assertEqual(common_type(INT, FLOAT), FLOAT)
        self.assertEqual(common_type(STRING, INT).kind, TypeKind.ANY)

    def test_optional_type_is_explicit_and_null_assignable(self):
        maybe_int = optional_of(INT)
        self.assertEqual(str(maybe_int), "int?")
        self.assertTrue(is_assignable(maybe_int, INT))
        self.assertTrue(is_assignable(maybe_int, NULL))
        self.assertFalse(is_assignable(INT, maybe_int))
        self.assertEqual(common_type(INT, maybe_int), maybe_int)

    def test_result_type_keeps_success_and_error_types(self):
        outcome = result_of(INT, STRING)
        self.assertEqual(str(outcome), "Hasil[int, string]")
        self.assertTrue(is_assignable(outcome, result_of(INT, STRING)))
        self.assertFalse(is_assignable(outcome, result_of(STRING, INT)))

    def test_named_struct_and_enum_are_nominal(self):
        account = struct_of("Akun", {"saldo": FLOAT, "aktif": BOOL})
        other_account = struct_of("Akun", {"saldo": FLOAT, "aktif": BOOL})
        other_shape = struct_of("Profil", {"saldo": FLOAT, "aktif": BOOL})
        status = enum_of("Status", ["Aktif", "Arsip"])
        self.assertEqual(str(account), "Akun")
        self.assertTrue(is_assignable(account, other_account))
        self.assertFalse(is_assignable(account, other_shape))
        self.assertEqual(status.variants, ("Aktif", "Arsip"))
        with self.assertRaises(ValueError):
            enum_of("Status", ["Aktif", "Aktif"])

    def test_builtin_registry_is_explicit(self):
        self.assertIsNotNone(get_builtin("panjang"))
        self.assertIsNone(get_builtin("akses_file"))
        self.assertEqual(call_builtin("panjang", [1, 2]), 2)
        self.assertEqual(call_builtin("maksimum", 3, 8), 8)
        self.assertGreaterEqual(len(BUILTINS), 8)

    def test_numeric_cast_rejects_boolean(self):
        with self.assertRaises(TypeError):
            call_builtin("bilangan", True)


if __name__ == "__main__":
    unittest.main()
