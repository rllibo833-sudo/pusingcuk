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

ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("PUSINGCUK_SAAS_DB", str(WEB_ROOT / "pusingcuk_saas.sqlite3")))
COOKIE_NAME = "pusingcuk_session"
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


def _cookie_value(handler: BaseHTTPRequestHandler) -> str | None:
    raw = handler.headers.get("Cookie", "")
    cookie = SimpleCookie()
    try:
        cookie.load(raw)
    except Exception:
        return None
    morsel = cookie.get(COOKIE_NAME)
    return morsel.value if morsel else None


def _current_user(handler: BaseHTTPRequestHandler) -> sqlite3.Row | None:
    token = _cookie_value(handler)
    if not token or not re.fullmatch(r"[A-Za-z0-9_-]{40,100}", token):
        return None
    now = int(time.time())
    with _db() as db:
        row = db.execute(
            "SELECT u.id,u.email,u.display_name FROM sessions s JOIN users u ON u.id=s.user_id "
            "WHERE s.token_hash=? AND s.expires_at>?", (_token_hash(token), now)
        ).fetchone()
    return row


def _issue_session(user_id: str) -> str:
    token = secrets.token_urlsafe(48)
    now = int(time.time())
    with _db() as db:
        db.execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
        db.execute("INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
                   (_token_hash(token), user_id, now, now + SESSION_TTL))
    return token


def _public_user(user: sqlite3.Row) -> dict[str, str]:
    return {"id": user["id"], "email": user["email"], "display_name": user["display_name"]}


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
        provider = GeminiGenerateContentProvider(
            api_key=os.environ.get("GEMINI_API_KEY", ""),
            model=model or "gemini-3.8-flash",
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
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def _cookie_headers(self, token: str | None, *, clear: bool = False) -> dict[str, str]:
        secure = os.environ.get("PUSINGCUK_SAAS_COOKIE_SECURE", "1") != "0"
        parts = [f"{COOKIE_NAME}={' ' if clear else token}", "Path=/", "HttpOnly", "SameSite=Strict"]
        if clear:
            parts[0] = f"{COOKIE_NAME}="
            parts.append("Max-Age=0")
        else:
            parts.append(f"Max-Age={SESSION_TTL}")
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
            with _db() as db:
                rows = db.execute(
                    "SELECT role,content,created_at FROM messages WHERE user_id=? "
                    "ORDER BY created_at DESC LIMIT 100", (user["id"],)
                ).fetchall()
            self._json(200, {"messages": [
                {"role": row["role"], "content": row["content"], "created_at": row["created_at"]}
                for row in reversed(rows)
            ]})
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
                salt = secrets.token_bytes(16)
                user_id = uuid.uuid4().hex
                with _db() as db:
                    try:
                        db.execute("INSERT INTO users(id,email,display_name,password_salt,password_hash,created_at) VALUES(?,?,?,?,?,?)",
                                   (user_id, email, name or email.split("@", 1)[0], salt, _password_hash(password, salt), int(time.time())))
                    except sqlite3.IntegrityError:
                        raise SaaSError("ACCOUNT_ALREADY_EXISTS", 409) from None
                token = _issue_session(user_id)
                with _db() as db:
                    user = db.execute("SELECT id,email,display_name FROM users WHERE id=?", (user_id,)).fetchone()
                self._json(201, {"user": _public_user(user)}, self._cookie_headers(token))
                return
            if path == "/api/auth/login":
                _rate_limit("login:" + (self.client_address[0] if self.client_address else "unknown"), 10)
                if set(payload) != {"email", "password"}:
                    raise SaaSError("AUTH_PAYLOAD_INVALID")
                email = payload["email"].strip().casefold() if isinstance(payload["email"], str) else ""
                password = payload["password"] if isinstance(payload["password"], str) else ""
                with _db() as db:
                    user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
                valid = False
                if user and len(password) <= 128:
                    valid = hmac.compare_digest(_password_hash(password, user["password_salt"]), user["password_hash"])
                if not valid:
                    raise SaaSError("INVALID_CREDENTIALS", 401)
                token = _issue_session(user["id"])
                self._json(200, {"user": _public_user(user)}, self._cookie_headers(token))
                return
            if path == "/api/auth/logout":
                token = _cookie_value(self)
                if token:
                    with _db() as db:
                        db.execute("DELETE FROM sessions WHERE token_hash=?", (_token_hash(token),))
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
                now = int(time.time())
                with _db() as db:
                    db.execute("INSERT INTO messages(id,user_id,role,content,created_at) VALUES(?,?,?,?,?)",
                               (uuid.uuid4().hex, user["id"], "user", query.strip(), now))
                    db.execute("INSERT INTO messages(id,user_id,role,content,created_at) VALUES(?,?,?,?,?)",
                               (uuid.uuid4().hex, user["id"], "assistant", answer[:8000], now))
                    db.execute("DELETE FROM messages WHERE user_id=? AND id NOT IN (SELECT id FROM messages WHERE user_id=? ORDER BY created_at DESC LIMIT 200)",
                               (user["id"], user["id"]))
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
        init_db()
        host = os.environ.get("PUSINGCUK_SAAS_BIND", "127.0.0.1")
        port = int(os.environ.get("PUSINGCUK_SAAS_PORT", os.environ.get("PORT", "8088")))
        if not 1 <= port <= 65535:
            raise ValueError("SAAS_PORT_INVALID")
        public_origin = os.environ.get("PUSINGCUK_SAAS_PUBLIC_ORIGIN", "").rstrip("/")
        local_dev_origin = public_origin in {"http://127.0.0.1:8088", "http://localhost:8088"} and os.environ.get("PUSINGCUK_SAAS_COOKIE_SECURE") == "0"
        if not public_origin.startswith("https://") and not local_dev_origin:
            raise ValueError("SAAS_PUBLIC_ORIGIN_MUST_BE_HTTPS")
        # Fail fast on provider configuration, but create a fresh assistant per user.
        _assistant_factory()
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
