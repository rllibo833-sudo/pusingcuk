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
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1] / "apps" / "pusingcuk-ai-saas" / "server.py"
SPEC = importlib.util.spec_from_file_location("pusingcuk_saas", SOURCE)
saas = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(saas)


class FakeAssistant:
    def __init__(self):
        self.last_style = None

    def ask(self, query, *, style="adaptif"):
        self.last_style = style
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
        self.fake_users = {}
        self.fake_tokens = {}
        self.fake_messages = []
        self.supabase_patch = patch.object(saas, "_supabase_request", side_effect=self.fake_supabase_request)
        self.supabase_patch.start()
        self.opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def fake_supabase_request(self, method, path, *, token=None, body=None):
        if path == "/auth/v1/signup" and method == "POST":
            email = body["email"].casefold()
            if email in self.fake_users:
                return 422, {"msg": "User already registered"}
            user = {"id": "user-" + str(len(self.fake_users) + 1), "email": email,
                    "password": body["password"], "user_metadata": body.get("data", {})}
            self.fake_users[email] = user
            access = "access-" + user["id"]
            refresh = "refresh-" + user["id"]
            self.fake_tokens[access] = user
            return 201, {"access_token": access, "refresh_token": refresh, "user": user}
        if path == "/auth/v1/token?grant_type=password" and method == "POST":
            user = self.fake_users.get(body["email"].casefold())
            if not user or user["password"] != body["password"]:
                return 400, {"msg": "Invalid login credentials"}
            access = "access-" + user["id"]
            refresh = "refresh-" + user["id"]
            self.fake_tokens[access] = user
            return 200, {"access_token": access, "refresh_token": refresh, "user": user}
        if path == "/auth/v1/user" and method == "GET":
            user = self.fake_tokens.get(token)
            if not user:
                return 401, {"msg": "Invalid token"}
            return 200, {key: value for key, value in user.items() if key != "password"}
        if path == "/auth/v1/logout" and method == "POST":
            return 204, {}
        if path == "/rest/v1/pusingcuk_saas_messages" and method == "POST":
            user = self.fake_tokens.get(token)
            if not user:
                return 401, {"message": "Unauthorized"}
            self.fake_messages.extend(body)
            return 201, {}
        if path.startswith("/rest/v1/pusingcuk_saas_messages?") and method == "GET":
            user = self.fake_tokens.get(token)
            if not user:
                return 401, {"message": "Unauthorized"}
            return 200, [{"role": item["role"], "content": item["content"],
                          "created_at": "2026-10-17T00:00:00+00:00"}
                         for item in self.fake_messages if item["user_id"] == user["id"]]
        if path.startswith("/auth/v1/token?grant_type=refresh_token") and method == "POST":
            user = next((u for u in self.fake_users.values() if "refresh-" + u["id"] == body.get("refresh_token")), None)
            if not user:
                return 401, {"msg": "Invalid refresh token"}
            access = "access-" + user["id"]
            self.fake_tokens[access] = user
            return 200, {"access_token": access, "refresh_token": body["refresh_token"]}
        return 404, {"message": "Mock Supabase endpoint not found"}

    def tearDown(self):
        self.supabase_patch.stop()
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
        status, _, body = self.request("/api/chat", {"query": "buat program .cuk", "style": "profesional"})
        self.assertEqual(status, 200, body)
        self.assertEqual(body["answer"], "Dijawab: buat program .cuk")
        self.assertEqual(next(iter(self.server._assistants.values())).last_style, "profesional")

        status, _, body = self.request("/api/chat", {"query": "halo", "style": "unregistered"})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "CHAT_STYLE_INVALID")
        status, _, body = self.request("/api/messages")
        self.assertEqual(status, 200)
        self.assertEqual([item["role"] for item in body["messages"]], ["user", "assistant"])
        self.assertEqual(body["messages"][0]["content"], "buat program .cuk")

    def test_workspace_retries_compiler_diagnostic_without_saving(self):
        self.assertEqual(self.register()[0], 201)
        assistant = self.server.assistant_for("user-1")
        assistant.ask = Mock(side_effect=[
            "Usulan awal. <CUK>print(1 + )</CUK>",
            "Diperbaiki berdasarkan diagnostik. <CUK>print(1 + 2)</CUK>",
        ])
        failed_check = {
            "ok": False, "error": "COMPILE_ERROR",
            "diagnostic": "baris 1: ekspresi tidak lengkap",
            "evidence_status": "DIAGNOSTIC_REAL", "diagnostic_location": {"line": 1, "column": 11},
            "failure_category": "syntax",
        }
        passed_check = {
            "ok": True, "error": None, "diagnostic": None,
            "evidence_status": "COMPILE_CHECK_PASSED", "diagnostic_location": None,
            "failure_category": None,
        }
        with patch("library.knowledge_grounding.load_index", return_value=[]), \
             patch("library.ai_tools.ToolRegistry.execute", side_effect=[failed_check, passed_check]) as compiler:
            status, _, body = self.request("/api/workspace/assist", {
                "request": "Buat penjumlahan sederhana", "source": ""
            })
        self.assertEqual(status, 200, body)
        self.assertEqual(body["candidate_source"], "print(1 + 2)\n")
        self.assertFalse(body["saved"])
        self.assertTrue(body["compile_check"]["ok"])
        self.assertEqual(body["compile_check"]["repair_attempts"], 1)
        self.assertEqual(body["compile_check"]["repair_stop_reason"], "compiler_passed")
        self.assertEqual(len(body["compile_check"]["compile_attempts"]), 2)
        self.assertEqual(compiler.call_count, 2)
        repair_prompt = assistant.ask.call_args_list[1].args[0]
        self.assertIn("ekspresi tidak lengkap", repair_prompt)

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
        self.assertIn('id="styleSelect"', html)
        self.assertIn('value="adaptif"', html)
        self.assertIn("localStorage.setItem('pusingcuk-chat-style',chatStyle)", html)
        self.assertIn("JSON.stringify({query,style:chatStyle})", html)
        self.assertIn('id="sourceEditor"', html)
        self.assertIn('id="codingRequest"', html)
        self.assertIn('id="assistBtn"', html)
        self.assertIn('id="checkBtn"', html)
        self.assertIn('id="saveFileBtn"', html)
        self.assertIn("/api/workspace/assist", html)
        self.assertIn("/api/workspace/check", html)
        self.assertIn("/api/project-files", html)
        server = SOURCE.read_text(encoding="utf-8")
        self.assertIn('if path == "/api/workspace/assist":', server)
        self.assertIn('if path == "/api/workspace/check":', server)
        self.assertIn('if path == "/api/projects":', server)
        self.assertIn('if path == "/api/project-files":', server)


if __name__ == "__main__":
    unittest.main()
