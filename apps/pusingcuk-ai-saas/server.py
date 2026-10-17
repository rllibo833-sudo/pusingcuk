"""PusingCuk AI SaaS MVP: account sessions + persistent chat over the existing assistant."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
import uuid
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import base64

ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("PUSINGCUK_SAAS_DB", str(WEB_ROOT / "pusingcuk_saas.sqlite3")))
COOKIE_NAME = "pusingcuk_session"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_PUBLISHABLE_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
SESSION_TTL = 60 * 60 * 24 * 14
MAX_BODY = 16 * 1024
PBKDF2_ROUNDS = 310_000
EMAIL_RE = re.compile(r"^[^\s@]{1,64}@[^\s@.]+(?:\.[^\s@.]+)+$")
RATE_BUCKETS: dict[str, list[float]] = {}
_RATE_GUARD = __import__("threading").Lock()


class SaaSError(Exception):
    def __init__(self, code: str, status: int = 400):
        super().__init__(code)
        self.code = code
        self.status = status


def _db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def init_db() -> None:
    with _db() as db:
        db.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
          display_name TEXT NOT NULL, password_salt BLOB NOT NULL,
          password_hash BLOB NOT NULL, created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
          token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          created_at INTEGER NOT NULL, expires_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS sessions_user_idx ON sessions(user_id);
        CREATE TABLE IF NOT EXISTS messages (
          id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          role TEXT NOT NULL CHECK(role IN ('user','assistant')),
          content TEXT NOT NULL CHECK(length(content) <= 8000), created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS messages_user_idx ON messages(user_id, created_at);
        """)


def _password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS)


def _rate_limit(key: str, limit: int, window: int = 60) -> None:
    now = time.monotonic()
    with _RATE_GUARD:
        recent = [stamp for stamp in RATE_BUCKETS.get(key, []) if now - stamp < window]
        if len(recent) >= limit:
            raise SaaSError("RATE_LIMITED", 429)
        recent.append(now)
        RATE_BUCKETS[key] = recent
        if len(RATE_BUCKETS) > 5000:
            for old_key in list(RATE_BUCKETS)[:1000]:
                RATE_BUCKETS.pop(old_key, None)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def _supabase_request(method: str, path: str, *, token: str | None = None, body: dict | list | None = None):
    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        raise SaaSError("SUPABASE_NOT_CONFIGURED", 503)
    payload = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"apikey": SUPABASE_PUBLISHABLE_KEY, "Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(SUPABASE_URL + path, data=payload, headers=headers, method=method)
    try:
        with urlopen(request, timeout=12) as response:
            raw = response.read(1000000)
            return response.status, json.loads(raw.decode("utf-8")) if raw else {}
    except HTTPError as exc:
        try:
            raw = exc.read(64000)
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            data = {}
        return exc.code, data
    except (URLError, TimeoutError, OSError):
        raise SaaSError("SUPABASE_UNAVAILABLE", 503) from None


def _session_from_cookie(handler: BaseHTTPRequestHandler) -> dict | None:
    cookie = SimpleCookie()
    try:
        cookie.load(handler.headers.get("Cookie", ""))
        morsel = cookie.get(COOKIE_NAME)
        if not morsel:
            return None
        value = morsel.value
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        session = json.loads(decoded.decode("utf-8"))
        return session if isinstance(session, dict) and isinstance(session.get("access_token"), str) else None
    except Exception:
        return None


def _encode_session(session: dict) -> str:
    raw = json.dumps({"access_token": session.get("access_token", ""),
                      "refresh_token": session.get("refresh_token", "")},
                     separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _current_user(handler: BaseHTTPRequestHandler) -> dict | None:
    session = getattr(handler, "_supabase_session", None) or _session_from_cookie(handler)
    if not session:
        return None
    try:
        status, result = _supabase_request("GET", "/auth/v1/user", token=session.get("access_token", ""))
        if status in (401, 403) and session.get("refresh_token"):
            status, refreshed = _supabase_request("POST", "/auth/v1/token?grant_type=refresh_token",
                                                  body={"refresh_token": session["refresh_token"]})
            if status == 200 and isinstance(refreshed, dict) and refreshed.get("access_token"):
                session = refreshed
                handler._supabase_session = session
                status, result = _supabase_request("GET", "/auth/v1/user", token=session["access_token"])
    except SaaSError:
        return None
    if status != 200 or not isinstance(result, dict) or not result.get("id"):
        return None
    handler._supabase_session = session
    metadata = result.get("user_metadata") if isinstance(result.get("user_metadata"), dict) else {}
    return {"id": result["id"], "email": result.get("email", ""),
            "display_name": metadata.get("display_name") or result.get("email", "").split("@", 1)[0]}


def _public_user(user: dict) -> dict[str, str]:
    return {"id": str(user["id"]), "email": str(user.get("email", "")),
            "display_name": str(user.get("display_name", ""))}


def _assistant_factory():
    from library.assistant import PusingCukAssistant
    from library.gemini_ai_provider import GeminiGenerateContentProvider
    from library.knowledge_grounding import load_index
    from library.local_ai_provider import LocalAIProviderError, OllamaChatProvider

    provider_name = os.environ.get("PUSINGCUK_AI_PROVIDER", "ollama").casefold()
    model = os.environ.get("PUSINGCUK_AI_MODEL")
    if provider_name == "ollama":
        provider = OllamaChatProvider(
            model=model or "qwen3:4b",
            endpoint=os.environ.get("PUSINGCUK_OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat"),
        )
    elif provider_name == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise SaaSError("AI_PROVIDER_NOT_CONFIGURED", 503)
        provider = GeminiGenerateContentProvider(
            api_key=api_key,
            model=model or "gemini-2.5-flash",
        )
    else:
        raise ValueError("SAAS_AI_PROVIDER_INVALID")
    documents = load_index(Path(os.environ.get("PUSINGCUK_AI_INDEX", str(ROOT / "library" / "knowledge_index.json"))))
    return PusingCukAssistant(provider, documents)


class Handler(BaseHTTPRequestHandler):
    server_version = "PusingCukSaaS"
    sys_version = ""

    def log_message(self, _format, *_args):
        # Never log request bodies, cookies, email addresses or prompts.
        return

    def _json(self, status: int, payload: dict, extra_headers: dict[str, str] | None = None) -> None:
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        headers = dict(extra_headers or {})
        refreshed = getattr(self, "_supabase_session", None)
        if refreshed and "Set-Cookie" not in headers:
            headers.update(self._cookie_headers(refreshed))
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def _cookie_headers(self, session: dict | None, *, clear: bool = False) -> dict[str, str]:
        secure = os.environ.get("PUSINGCUK_SAAS_COOKIE_SECURE", "1") != "0"
        value = "" if clear or not session else _encode_session(session)
        parts = [f"{COOKIE_NAME}={value}", "Path=/", "HttpOnly", "SameSite=Strict"]
        parts.append("Max-Age=0" if clear else f"Max-Age={SESSION_TTL}")
        if secure:
            parts.append("Secure")
        return {"Set-Cookie": "; ".join(parts)}

    def _check_origin(self) -> None:
        expected = os.environ.get("PUSINGCUK_SAAS_PUBLIC_ORIGIN", "").rstrip("/")
        origin = self.headers.get("Origin", "").rstrip("/")
        if not expected or not origin or not hmac.compare_digest(origin, expected):
            raise SaaSError("ORIGIN_NOT_ALLOWED", 403)

    def _read_json(self) -> dict:
        if self.headers.get_content_type().casefold() != "application/json":
            raise SaaSError("JSON_REQUIRED", 415)
        if self.headers.get("Transfer-Encoding") is not None:
            raise SaaSError("TRANSFER_ENCODING_UNSUPPORTED", 400)
        raw_length = self.headers.get("Content-Length", "")
        if not raw_length.isascii() or not raw_length.isdecimal():
            raise SaaSError("CONTENT_LENGTH_REQUIRED", 411)
        length = int(raw_length)
        if length > MAX_BODY:
            raise SaaSError("REQUEST_TOO_LARGE", 413)
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError()
            value = json.loads(raw.decode("utf-8"), object_pairs_hook=self._unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            raise SaaSError("JSON_INVALID", 400) from None
        if not isinstance(value, dict):
            raise SaaSError("JSON_OBJECT_REQUIRED", 400)
        return value

    @staticmethod
    def _unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    def _auth_required(self):
        user = _current_user(self)
        if user is None:
            raise SaaSError("AUTH_REQUIRED", 401)
        return user

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/auth/me":
            user = _current_user(self)
            if user is None:
                self._json(401, {"error": "AUTH_REQUIRED"})
            else:
                self._json(200, {"user": _public_user(user)})
            return
        if path == "/api/messages":
            user = _current_user(self)
            if user is None:
                self._json(401, {"error": "AUTH_REQUIRED"})
                return
            session = getattr(self, "_supabase_session", None) or _session_from_cookie(self)
            status, rows = _supabase_request(
                "GET", "/rest/v1/pusingcuk_saas_messages?select=role,content,created_at&order=created_at.asc&limit=100",
                token=session.get("access_token", "") if session else "")
            if status != 200 or not isinstance(rows, list):
                raise SaaSError("MESSAGE_STORAGE_UNAVAILABLE", 503)
            self._json(200, {"messages": rows})
            return
        if path == "/healthz":
            self._json(200, {"status": "ok"})
            return
        if path.startswith("/api/"):
            self._json(404, {"error": "NOT_FOUND"})
            return
        target = (WEB_ROOT / ("index.html" if path == "/" else path.lstrip("/"))).resolve()
        if WEB_ROOT.resolve() not in target.parents and target != WEB_ROOT.resolve():
            self._json(404, {"error": "NOT_FOUND"})
            return
        if not target.is_file():
            self._json(404, {"error": "NOT_FOUND"})
            return
        if target.suffix != ".html":
            self._json(404, {"error": "NOT_FOUND"})
            return
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        request_id = uuid.uuid4().hex
        try:
            self._check_origin()
            path = urlsplit(self.path).path
            if urlsplit(self.path).query or urlsplit(self.path).fragment:
                raise SaaSError("NOT_FOUND", 404)
            payload = self._read_json()
            if path == "/api/auth/register":
                _rate_limit("register:" + (self.client_address[0] if self.client_address else "unknown"), 5)
                if set(payload) != {"email", "password", "display_name"}:
                    raise SaaSError("AUTH_PAYLOAD_INVALID")
                email = payload["email"].strip().casefold() if isinstance(payload["email"], str) else ""
                password = payload["password"] if isinstance(payload["password"], str) else ""
                name = payload["display_name"].strip() if isinstance(payload["display_name"], str) else ""
                if len(email) > 254 or not EMAIL_RE.fullmatch(email):
                    raise SaaSError("EMAIL_INVALID")
                if len(password) < 12 or len(password) > 128:
                    raise SaaSError("PASSWORD_LENGTH_INVALID")
                if len(name) > 80:
                    raise SaaSError("DISPLAY_NAME_INVALID")
                status, result = _supabase_request("POST", "/auth/v1/signup",
                    body={"email": email, "password": password,
                          "data": {"display_name": name or email.split("@", 1)[0]}})
                if status not in (200, 201) or not isinstance(result, dict):
                    message = str(result.get("msg") or result.get("message") or result.get("error_description") or "")
                    if status == 422 and ("already" in message.casefold() or "registered" in message.casefold()):
                        raise SaaSError("ACCOUNT_ALREADY_EXISTS", 409)
                    if status in (400, 422):
                        raise SaaSError("REGISTRATION_REJECTED")
                    raise SaaSError("SUPABASE_AUTH_UNAVAILABLE", 503)
                session = result if result.get("access_token") else result.get("session")
                if not isinstance(session, dict) or not session.get("access_token"):
                    self._json(202, {"confirmation_required": True,
                        "message": "Akun dibuat. Periksa email untuk konfirmasi, lalu masuk."})
                    return
                status, profile = _supabase_request("GET", "/auth/v1/user", token=session["access_token"])
                if status != 200 or not isinstance(profile, dict) or not profile.get("id"):
                    raise SaaSError("SUPABASE_AUTH_UNAVAILABLE", 503)
                metadata = profile.get("user_metadata") if isinstance(profile.get("user_metadata"), dict) else {}
                user = {"id": profile["id"], "email": profile.get("email", email),
                        "display_name": metadata.get("display_name") or name or email.split("@", 1)[0]}
                self._json(201, {"user": _public_user(user)}, self._cookie_headers(session))
                return
            if path == "/api/auth/login":
                _rate_limit("login:" + (self.client_address[0] if self.client_address else "unknown"), 10)
                if set(payload) != {"email", "password"}:
                    raise SaaSError("AUTH_PAYLOAD_INVALID")
                email = payload["email"].strip().casefold() if isinstance(payload["email"], str) else ""
                password = payload["password"] if isinstance(payload["password"], str) else ""
                if not EMAIL_RE.fullmatch(email) or len(password) > 128 or not password:
                    raise SaaSError("INVALID_CREDENTIALS", 401)
                status, session = _supabase_request("POST", "/auth/v1/token?grant_type=password",
                                                     body={"email": email, "password": password})
                if status != 200 or not isinstance(session, dict) or not session.get("access_token"):
                    raise SaaSError("INVALID_CREDENTIALS", 401)
                status, profile = _supabase_request("GET", "/auth/v1/user", token=session["access_token"])
                if status != 200 or not isinstance(profile, dict) or not profile.get("id"):
                    raise SaaSError("INVALID_CREDENTIALS", 401)
                metadata = profile.get("user_metadata") if isinstance(profile.get("user_metadata"), dict) else {}
                user = {"id": profile["id"], "email": profile.get("email", email),
                        "display_name": metadata.get("display_name") or email.split("@", 1)[0]}
                self._json(200, {"user": _public_user(user)}, self._cookie_headers(session))
                return
            if path == "/api/auth/logout":
                session = _session_from_cookie(self)
                if session and session.get("access_token"):
                    try:
                        _supabase_request("POST", "/auth/v1/logout", token=session["access_token"], body={})
                    except SaaSError:
                        pass
                self._json(200, {"ok": True}, self._cookie_headers(None, clear=True))
                return
            if path == "/api/chat":
                user = self._auth_required()
                _rate_limit("chat:" + user["id"], 20)
                if set(payload) not in ({"query"}, {"query", "style"}):
                    raise SaaSError("CHAT_PAYLOAD_INVALID")
                query = payload["query"]
                if not isinstance(query, str) or not query.strip() or len(query) > 300:
                    raise SaaSError("QUERY_INVALID")
                style = payload.get("style", "adaptif")
                if not isinstance(style, str) or style not in {"adaptif", "genz", "normal", "formal", "profesional"}:
                    raise SaaSError("CHAT_STYLE_INVALID")
                # A bounded in-memory assistant per authenticated user keeps turn history isolated.
                assistant = self.server.assistant_for(user["id"])
                user_lock, slot = self.server.acquire_turn(user["id"])
                if user_lock is None:
                    raise SaaSError("AI_BUSY", 503)
                try:
                    answer = assistant.ask(query.strip(), style=style)
                except Exception:
                    self._json(502, {"error": "AI_PROVIDER_FAILURE", "request_id": request_id})
                    return
                finally:
                    user_lock.release()
                    slot.release()
                session = getattr(self, "_supabase_session", None) or _session_from_cookie(self)
                if not session:
                    raise SaaSError("AUTH_REQUIRED", 401)
                status, _ = _supabase_request("POST", "/rest/v1/pusingcuk_saas_messages",
                    token=session.get("access_token", ""),
                    body=[{"user_id": user["id"], "role": "user", "content": query.strip()},
                          {"user_id": user["id"], "role": "assistant", "content": answer[:8000]}])
                if status not in (200, 201, 204):
                    raise SaaSError("MESSAGE_STORAGE_UNAVAILABLE", 503)
                self._json(200, {"request_id": request_id, "answer": answer})
                return
            self._json(404, {"error": "NOT_FOUND", "request_id": request_id})
        except SaaSError as exc:
            self._json(exc.status, {"error": exc.code, "request_id": request_id})
        except (OSError, sqlite3.Error):
            self._json(503, {"error": "STORAGE_UNAVAILABLE", "request_id": request_id})
        except Exception:
            self._json(500, {"error": "INTERNAL_ERROR", "request_id": request_id})

    def do_OPTIONS(self):
        self._json(405, {"error": "METHOD_NOT_ALLOWED"}, {"Allow": "GET, POST"})

    do_PUT = do_OPTIONS
    do_PATCH = do_OPTIONS
    do_DELETE = do_OPTIONS


class SaaSServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, handler):
        super().__init__(address, handler)
        self._assistants = {}
        self._assistant_locks = {}
        self._assistant_lock = __import__("threading").Lock()
        self._slots = __import__("threading").BoundedSemaphore(4)

    def assistant_for(self, user_id):
        with self._assistant_lock:
            if user_id not in self._assistants:
                if len(self._assistants) >= 128:
                    raise SaaSError("AI_CAPACITY_REACHED", 503)
                self._assistants[user_id] = _assistant_factory()
                self._assistant_locks[user_id] = __import__("threading").Lock()
            return self._assistants[user_id]

    def acquire_turn(self, user_id):
        if not self._slots.acquire(blocking=False):
            return None, None
        with self._assistant_lock:
            lock = self._assistant_locks.get(user_id)
        if lock is None or not lock.acquire(blocking=False):
            self._slots.release()
            return None, None
        return lock, self._slots


def main() -> int:
    try:
        host = os.environ.get("PUSINGCUK_SAAS_BIND", "127.0.0.1")
        port = int(os.environ.get("PUSINGCUK_SAAS_PORT", os.environ.get("PORT", "8088")))
        if not 1 <= port <= 65535:
            raise ValueError("SAAS_PORT_INVALID")
        public_origin = os.environ.get("PUSINGCUK_SAAS_PUBLIC_ORIGIN", "").rstrip("/")
        local_dev_origin = public_origin in {"http://127.0.0.1:8088", "http://localhost:8088"} and os.environ.get("PUSINGCUK_SAAS_COOKIE_SECURE") == "0"
        if public_origin and not public_origin.startswith("https://") and not local_dev_origin:
            raise ValueError("SAAS_PUBLIC_ORIGIN_MUST_BE_HTTPS")
        if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
            raise ValueError("SUPABASE_CONFIGURATION_REQUIRED")
        server = SaaSServer((host, port), Handler)
    except Exception as exc:
        print("PusingCuk AI SaaS belum siap: " + getattr(exc, "code", str(exc)))
        return 2
    print(f"PusingCuk AI SaaS listening on {host}:{port}; TLS must be terminated by a trusted HTTPS reverse proxy.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
