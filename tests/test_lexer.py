import unittest

from lexer import Lexer, LexerError, lex


class TestLexer(unittest.TestCase):
    def test_keywords_and_identifiers(self):
        tokens = lex("jancuk\nlah umur = 20\nselesai jancuk")
        meaningful = [
            (token.kind, token.value)
            for token in tokens
            if token.kind not in ("NEWLINE", "EOF")
        ]

        self.assertEqual(
            meaningful,
            [
                ("KEYWORD", "jancuk"),
                ("KEYWORD", "lah"),
                ("IDENT", "umur"),
                ("OP", "="),
                ("INTEGER", 20),
                ("KEYWORD", "selesai"),
                ("KEYWORD", "jancuk"),
            ],
        )

    def test_all_operators_use_longest_match(self):
        tokens = lex("== != <= >= // + - * / % < >")
        operators = [
            token.value for token in tokens
            if token.kind == "OP"
        ]

        self.assertEqual(
            operators,
            ["==", "!=", "<=", ">=", "//",
             "+", "-", "*", "/", "%", "<", ">"],
        )

    def test_numbers_and_negative_operator(self):
        tokens = lex("12 3.5 -7")
        values = [
            (token.kind, token.value)
            for token in tokens
            if token.kind != "EOF"
        ]

        self.assertEqual(
            values,
            [
                ("INTEGER", 12),
                ("FLOAT", 3.5),
                ("OP", "-"),
                ("INTEGER", 7),
            ],
        )

    def test_list_and_function_punctuation(self):
        tokens = lex("panjang([10, 20])")
        values = [
            token.value for token in tokens
            if token.kind != "EOF"
        ]

        self.assertEqual(
            values,
            ["panjang", "(", "[", 10, ",", 20, "]", ")"],
        )

    def test_string_and_escape_sequences(self):
        tokens = lex(r'"halo\n dunia"')
        self.assertEqual(tokens[0].kind, "STRING")
        self.assertEqual(tokens[0].value, "halo\n dunia")

    def test_single_quoted_string(self):
        tokens = lex("'Pusingcuk'")
        self.assertEqual(tokens[0].value, "Pusingcuk")

    def test_comments_preserve_newline(self):
        tokens = lex("lah x = 1 # komentar\nhedeh x")
        newlines = [
            token for token in tokens
            if token.kind == "NEWLINE"
        ]

        self.assertEqual(len(newlines), 1)
        self.assertEqual(newlines[0].line, 1)

    def test_line_numbers(self):
        tokens = lex("lah x = 1\nhedeh x")
        output = next(
            token for token in tokens
            if token.value == "hedeh"
        )

        self.assertEqual(output.line, 2)
        self.assertEqual(output.column, 1)

    def test_unterminated_string(self):
        with self.assertRaisesRegex(
            LexerError, "string belum ditutup"
        ):
            lex('"belum selesai')

    def test_unknown_character(self):
        with self.assertRaisesRegex(
            LexerError, "karakter tidak dikenal"
        ):
            lex("lah x = @")

    def test_unknown_escape(self):
        with self.assertRaisesRegex(
            LexerError, "escape tidak dikenal"
        ):
            lex(r'"salah\q"')

    def test_empty_source_has_eof(self):
        tokens = lex("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].kind, "EOF")


if __name__ == "__main__":
    unittest.main()
