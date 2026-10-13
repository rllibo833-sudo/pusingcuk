"""Tests for actionable parser diagnostics and source coordinates."""
import unittest

from parser import ParserError, parse


class ParserDiagnosticTests(unittest.TestCase):
    def test_invalid_expression_reports_file_line_column_snippet_and_suggestion(self):
        source = "jancuk\nhedeh 1 +\nselesai jancuk"
        with self.assertRaises(ParserError) as caught:
            parse(source, filename="contoh.cuk")
        message = str(caught.exception)
        self.assertIn("[contoh.cuk] Baris 2, kolom", message)
        self.assertIn("Kesalahan sintaks", message)
        self.assertIn("hedeh 1 +", message)
        self.assertIn("^", message)
        self.assertIn("Saran:", message)
        self.assertNotIn("sintaks lu typo cuk", message)

    def test_balek_error_keeps_specific_correction(self):
        source = "jancuk\nfungsi nilai()\nbalek\nselesai fungsi\nselesai jancuk"
        with self.assertRaises(ParserError) as caught:
            parse(source)
        message = str(caught.exception)
        self.assertIn("balek butuh ekspresi", message)
        self.assertIn("Tambahkan nilai setelah 'balek'", message)

    def test_missing_block_keyword_gives_expected_token(self):
        source = "jancuk\nselesai njir\nselesai jancuk"
        with self.assertRaises(ParserError) as caught:
            parse(source)
        self.assertIn("mengharapkan", str(caught.exception))
        self.assertIn("Saran:", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
