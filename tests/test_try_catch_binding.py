"""Reference-runtime tests for scoped error-message binding in ketangkep."""
from contextlib import redirect_stdout
from io import StringIO
import unittest

from evaluator import run


class CatchBindingTests(unittest.TestCase):
    def test_catch_variable_contains_exception_message_and_is_local(self):
        source = """jancuk
lah pesan = \"nilai-luar\"
coba
    hedeh tidak_ada
ketangkep pesan
    hedeh pesan
selesai coba
hedeh pesan
selesai jancuk
"""
        output = StringIO()
        with redirect_stdout(output):
            run(source)
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("tidak_ada", lines[0])
        self.assertIn("belum dibuat", lines[0])
        self.assertEqual(lines[1], "nilai-luar")


if __name__ == "__main__":
    unittest.main()
