"""Integration checks for the PusingCuk AI SaaS HTTP boundary.

These tests use a fake assistant and temporary SQLite database. They do not
claim that a real model provider or generated .cuk runtime was exercised.
"""
import http.cookiejar
import importlib.util
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "apps" / "pusingcuk-ai-saas" / "server.py"
SPEC = importlib.util.spec_from_file_location("pusingcuk_saas", SOURCE)
saas = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(saas)


class FakeAssistant:
    def ask(self, query):
        return "Dijawab: " + query


class SaaSHttpFlowTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.old_db_path = saas.DB_PATH
        saas.DB_PATH = Path(self.tempdir.name) / "test.sqlite3"
        saas.init_db()
        saas.RATE_BUCKETS.clear()
        self.server = saas.SaaSServer(("127.0.0.1", 0), saas.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.origin = "http://127.0.0.1:" + str(self.server.server_address[1])
        self.env_patch = patch.dict(os.environ, {
            "PUSINGCUK_SAAS_PUBLIC_ORIGIN": self.origin,
            "PUSINGCUK_SAAS_COOKIE_SECURE": "0",
        })
        self.env_patch.start()
        self.assistant_patch = patch.object(saas, "_assistant_factory", side_effect=FakeAssistant)
        self.assistant_patch.start()
        self.opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def tearDown(self):
        self.assistant_patch.stop()
        self.env_patch.stop()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        saas.DB_PATH = self.old_db_path
        self.tempdir.cleanup()
        saas.RATE_BUCKETS.clear()

    def request(self, path, payload=None, *, origin=None):
        headers = {}
        data = None
        method = "GET"
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
            headers["Origin"] = self.origin if origin is None else origin
            method = "POST"
        req = Request(self.origin + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=3) as response:
                return response.status, response.headers, json.loads(response.read())
        except HTTPError as error:
            return error.code, error.headers, json.loads(error.read())

    def register(self, email="user@example.com"):
        return self.request("/api/auth/register", {
            "email": email, "password": "a-long-test-password", "display_name": "Pengguna"
        })

    def test_register_login_and_session_identity(self):
        status, headers, body = self.register()
        self.assertEqual(status, 201, body)
        registered_id = body["user"]["id"]
        self.assertIn("HttpOnly", headers.get("Set-Cookie", ""))
        self.assertIn("pusingcuk_session=", headers.get("Set-Cookie", ""))
        self.assertEqual(body["user"]["email"], "user@example.com")
        status, _, body = self.request("/api/auth/me")
        self.assertEqual(status, 200)
        self.assertEqual(body["user"]["id"], registered_id)

        status, _, _ = self.request("/api/auth/logout", {})
        self.assertEqual(status, 200)
        status, _, _ = self.request("/api/auth/me")
        self.assertEqual(status, 401)

        status, _, body = self.request("/api/auth/login", {
            "email": "USER@example.com", "password": "a-long-test-password"
        })
        self.assertEqual(status, 200, body)
        status, _, body = self.request("/api/auth/me")
        self.assertEqual(status, 200)
        self.assertEqual(body["user"]["id"], registered_id)

    def test_duplicate_account_and_invalid_credentials_are_rejected(self):
        self.assertEqual(self.register()[0], 201)
        status, _, body = self.register("USER@example.com")
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "ACCOUNT_ALREADY_EXISTS")
        status, _, body = self.request("/api/auth/login", {
            "email": "user@example.com", "password": "wrong-password"
        })
        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "INVALID_CREDENTIALS")

    def test_chat_persists_transcript_and_requires_authentication(self):
        status, _, body = self.request("/api/chat", {"query": "halo"})
        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "AUTH_REQUIRED")
        self.assertEqual(self.register()[0], 201)
        status, _, body = self.request("/api/chat", {"query": "buat program .cuk"})
        self.assertEqual(status, 200, body)
        self.assertEqual(body["answer"], "Dijawab: buat program .cuk")
        status, _, body = self.request("/api/messages")
        self.assertEqual(status, 200)
        self.assertEqual([item["role"] for item in body["messages"]], ["user", "assistant"])
        self.assertEqual(body["messages"][0]["content"], "buat program .cuk")

    def test_post_rejects_wrong_origin_and_oversized_body(self):
        status, _, body = self.request("/api/auth/register", {
            "email": "user@example.com", "password": "a-long-test-password", "display_name": "U"
        }, origin="https://attacker.example")
        self.assertEqual(status, 403)
        self.assertEqual(body["error"], "ORIGIN_NOT_ALLOWED")

        req = Request(self.origin + "/api/auth/register", data=b" " * (saas.MAX_BODY + 1),
                      headers={"Content-Type": "application/json", "Origin": self.origin},
                      method="POST")
        try:
            self.opener.open(req, timeout=3)
            self.fail("Oversized request should have been rejected")
        except HTTPError as error:
            self.assertEqual(error.code, 413)


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

    def test_workspace_inline_javascript_has_no_escaped_code_separator(self):
        html = (Path(__file__).resolve().parents[1] / "apps" / "pusingcuk-ai-saas" / "index.html").read_text(encoding="utf-8")
        # A literal backslash-n between JS declarations is not a JavaScript line break
        # and makes the entire inline script fail to parse in the browser.
        self.assertNotIn(r"\nasync function loadHistory", html)
        self.assertIn("\nasync function loadHistory", html)


if __name__ == "__main__":
    unittest.main()
