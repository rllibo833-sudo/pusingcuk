"""Focused unit checks for the PusingCuk AI SaaS account primitives."""
import importlib.util
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "apps" / "pusingcuk-ai-saas" / "server.py"
SPEC = importlib.util.spec_from_file_location("pusingcuk_saas", SOURCE)
saas = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(saas)


class SaaSPrimitiveTests(unittest.TestCase):
    def test_password_hash_is_salted_and_repeatable(self):
        salt = b"1234567890123456"
        first = saas._password_hash("example-password", salt)
        self.assertEqual(first, saas._password_hash("example-password", salt))
        self.assertNotEqual(first, saas._password_hash("different-password", salt))
        self.assertNotEqual(first, saas._password_hash("example-password", b"abcdefghijklmnop"))

    def test_session_tokens_are_stored_as_hashes(self):
        token = "a" * 48
        self.assertNotEqual(token, saas._token_hash(token))
        self.assertEqual(saas._token_hash(token), saas._token_hash(token))


if __name__ == "__main__":
    unittest.main()
