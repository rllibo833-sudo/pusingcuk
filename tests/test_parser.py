import unittest
from parser import parse, ParserError


class ParserTests(unittest.TestCase):
    def test_program_declaration_and_print(self):
        tree = parse("jancuk\nlah angka = 12\nhedeh angka\nselesai jancuk")
        self.assertEqual(tree.kind, "Program")
        self.assertEqual([n.kind for n in tree.body], ["Declare", "Print"])
        self.assertEqual(tree.body[0].name, "angka")
        self.assertEqual(tree.body[0].value.value, 12)

    def test_operator_precedence(self):
        tree = parse("jancuk\nlah x = 2 + 3 * 4\nselesai jancuk")
        expr = tree.body[0].value
        self.assertEqual(expr.op, "+")
        self.assertEqual(expr.right.op, "*")

    def test_assignment(self):
        tree = parse("jancuk\nlah x = 1\nx = x + 1\nselesai jancuk")
        self.assertEqual(tree.body[1].kind, "Assign")

    def test_if_else(self):
        src = "jancuk\nnjir benar\nhedeh 1\nkampret\nhedeh 2\nselesai njir\nselesai jancuk"
        tree = parse(src)
        self.assertEqual(tree.body[0].kind, "If")
        self.assertEqual(len(tree.body[0].else_body), 1)

    def test_while(self):
        tree = parse("jancuk\nmumet salah\nhedeh 1\nselesai mumet\nselesai jancuk")
        self.assertEqual(tree.body[0].kind, "While")

    def test_function(self):
        src = "jancuk\nfungsi tambah(a, b)\nbalek a + b\nselesai fungsi\nselesai jancuk"
        tree = parse(src)
        self.assertEqual(tree.body[0].kind, "Function")
        self.assertEqual(tree.body[0].params, ["a", "b"])
        self.assertEqual(tree.body[0].body[0].kind, "Return")

    def test_list_and_call(self):
        tree = parse("jancuk\nlah xs = [1, 2]\nlah n = panjang(xs)\nselesai jancuk")
        self.assertEqual(tree.body[0].value.kind, "List")
        self.assertEqual(tree.body[1].value.kind, "Call")

    def test_missing_program_end(self):
        with self.assertRaises(ParserError):
            parse("jancuk\nlah x = 1")



    def test_balek_without_expression_is_a_controlled_parse_error(self):
        source = "jancuk\nfungsi ambil()\nbalek\nselesai fungsi\nselesai jancuk"
        with self.assertRaises(ParserError) as caught:
            parse(source)
        self.assertIn("balek butuh ekspresi", str(caught.exception))


if __name__ == "__main__":
    unittest.main()


class ParserIndexTests(unittest.TestCase):
    def test_parser_list_index_read(self):
        tree = parse("jancuk\nlah data = [10, 20]\nhedeh data[0]\nselesai jancuk")
        expr = tree.body[1].value
        self.assertEqual(expr.kind, "Index")
        self.assertEqual(expr.collection.name, "data")
        self.assertEqual(expr.index.value, 0)

    def test_parser_list_index_assignment(self):
        tree = parse("jancuk\nlah data = [10, 20]\ndata[0] = 99\nselesai jancuk")
        stmt = tree.body[1]
        self.assertEqual(stmt.kind, "IndexAssign")
        self.assertEqual(stmt.collection.name, "data")
        self.assertEqual(stmt.index.value, 0)
        self.assertEqual(stmt.value.value, 99)

    def test_parser_nested_index(self):
        tree = parse("jancuk\nlah data = [[1, 2], [3, 4]]\nhedeh data[1][0]\nselesai jancuk")
        expr = tree.body[1].value
        self.assertEqual(expr.kind, "Index")
        self.assertEqual(expr.index.value, 0)
        self.assertEqual(expr.collection.kind, "Index")
