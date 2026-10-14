"""Loopback-only authenticated HTTP adapter for the experimental PusingCuk AI CLI."""
from __future__ import annotations

import hmac
import ipaddress
import json
import os
import re
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

from library.assistant import PusingCukAssistant
from library.gemini_ai_provider import GeminiGenerateContentProvider
from library.knowledge_grounding import load_index
from library.local_ai_provider import LocalAIProviderError, OllamaChatProvider

MAX_REQUEST_BYTES = 4096
MAX_RESPONSE_BYTES = 16384
MAX_SESSIONS = 64
MAX_CONCURRENT_REQUESTS = 4
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")


class _Session:
    def __init__(self, assistant: Any) -> None:
        self.assistant = assistant
        self.lock = threading.Lock()
        self.last_used = time.monotonic()


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], token: str, factory: Callable[[], Any]) -> None:
        self.token = token
        self.factory = factory
        self.sessions: dict[str, _Session] = {}
        self.sessions_guard = threading.Lock()
        self.slots = threading.BoundedSemaphore(MAX_CONCURRENT_REQUESTS)
        super().__init__(address, _Handler)

    def acquire_session(self, session_id: str) -> _Session | None:
        # All session locks are acquired while the table guard is held, so an
        # in-flight session cannot be evicted and one session cannot race itself.
        with self.sessions_guard:
            session = self.sessions.get(session_id)
            if session is None:
                if len(self.sessions) >= MAX_SESSIONS:
                    idle = sorted(
                        (entry.last_used, key)
                        for key, entry in self.sessions.items()
                        if not entry.lock.locked()
                    )
                    if not idle:
                        return None
                    del self.sessions[idle[0][1]]
                session = _Session(self.factory())
                self.sessions[session_id] = session
            if not session.lock.acquire(blocking=False):
                return None
            session.last_used = time.monotonic()
            return session


class _Handler(BaseHTTPRequestHandler):
    server: _Server
    server_version = "PusingCukAI"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(5.0)

    def log_message(self, _format: str, *_args: Any) -> None:
        # No client address, session ID, query, or token in default logs.
        return

    def _json(self, status: int, data: dict[str, Any], headers: dict[str, str] | None = None) -> None:
        body = json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
        if len(body) > MAX_RESPONSE_BYTES:
            status, body = 502, b'{"error":"AI_SERVICE_RESPONSE_TOO_LARGE"}'
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        del message, explain
        self._json(405 if code in (405, 501) else code,
                   {"error": "AI_SERVICE_METHOD_NOT_ALLOWED" if code in (405, 501) else "AI_SERVICE_REQUEST_INVALID"})

    def do_GET(self) -> None:
        try:
            path = urlsplit(self.path)
        except ValueError:
            self._json(404, {"error": "AI_SERVICE_ROUTE_NOT_FOUND"})
            return
        if path.path == "/healthz" and not path.query and not path.fragment:
            # Liveness only: no inference/readiness promise.
            self._json(200, {"status": "ok"})
        else:
            self._json(404, {"error": "AI_SERVICE_ROUTE_NOT_FOUND"})

    def do_POST(self) -> None:
        request_id = uuid.uuid4().hex
        try:
            path = urlsplit(self.path)
        except ValueError:
            self._json(404, {"error": "AI_SERVICE_ROUTE_NOT_FOUND", "request_id": request_id})
            return
        if path.path != "/v1/chat" or path.query or path.fragment:
            self._json(404, {"error": "AI_SERVICE_ROUTE_NOT_FOUND", "request_id": request_id})
            return

        auth = self.headers.get_all("Authorization", [])
        if len(auth) != 1 or not auth[0].startswith("Bearer ") or not hmac.compare_digest(auth[0][7:], self.server.token):
            self._json(401, {"error": "AI_SERVICE_UNAUTHORIZED", "request_id": request_id},
                       {"WWW-Authenticate": "Bearer"})
            return
        if self.headers.get("Transfer-Encoding") is not None:
            self._json(400, {"error": "AI_SERVICE_TRANSFER_ENCODING_UNSUPPORTED", "request_id": request_id})
            return
        if self.headers.get("Content-Encoding", "identity").casefold() != "identity":
            self._json(415, {"error": "AI_SERVICE_CONTENT_ENCODING_UNSUPPORTED", "request_id": request_id})
            return
        if self.headers.get_content_type().casefold() != "application/json":
            self._json(415, {"error": "AI_SERVICE_JSON_REQUIRED", "request_id": request_id})
            return

        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or not re.fullmatch(r"[0-9]{1,10}", lengths[0]):
            self._json(411, {"error": "AI_SERVICE_CONTENT_LENGTH_REQUIRED", "request_id": request_id})
            return
        size = int(lengths[0])
        if size > MAX_REQUEST_BYTES:
            self._json(413, {"error": "AI_SERVICE_REQUEST_TOO_LARGE", "request_id": request_id})
            return
        try:
            raw = self.rfile.read(size)
            if len(raw) != size:
                self._json(400, {"error": "AI_SERVICE_BODY_TRUNCATED", "request_id": request_id})
                return

            def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
                value: dict[str, Any] = {}
                for key, item in pairs:
                    if key in value:
                        raise ValueError("duplicate JSON key")
                    value[key] = item
                return value

            payload = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
        except (UnicodeError, json.JSONDecodeError, ValueError):
            self._json(400, {"error": "AI_SERVICE_JSON_INVALID", "request_id": request_id})
            return

        if not isinstance(payload, dict) or set(payload) != {"session_id", "query"}:
            self._json(400, {"error": "AI_SERVICE_REQUEST_SCHEMA_INVALID", "request_id": request_id})
            return
        session_id, query = payload["session_id"], payload["query"]
        if not isinstance(session_id, str) or not SESSION_ID_RE.fullmatch(session_id):
            self._json(400, {"error": "AI_SERVICE_SESSION_ID_INVALID", "request_id": request_id})
            return
        if not isinstance(query, str) or not query.strip() or len(query) > 300:
            self._json(400, {"error": "AI_SERVICE_QUERY_INVALID", "request_id": request_id})
            return

        if not self.server.slots.acquire(blocking=False):
            self._json(503, {"error": "AI_SERVICE_BUSY", "request_id": request_id}, {"Retry-After": "1"})
            return
        session: _Session | None = None
        try:
            try:
                session = self.server.acquire_session(session_id)
            except Exception:
                self._json(502, {"error": "AI_SERVICE_PROVIDER_FAILURE", "request_id": request_id})
                return
            if session is None:
                self._json(503, {"error": "AI_SERVICE_SESSION_BUSY", "request_id": request_id},
                           {"Retry-After": "1"})
                return
            try:
                answer = session.assistant.ask(query)
            except ValueError:
                self._json(400, {"error": "AI_SERVICE_QUERY_INVALID", "request_id": request_id})
                return
            except Exception:
                self._json(502, {"error": "AI_SERVICE_PROVIDER_FAILURE", "request_id": request_id})
                return
            if not isinstance(answer, str) or not answer.strip():
                self._json(502, {"error": "AI_SERVICE_EMPTY_ANSWER", "request_id": request_id})
                return
            self._json(200, {"request_id": request_id, "session_id": session_id, "answer": answer})
        finally:
            if session is not None:
                with self.server.sessions_guard:
                    session.last_used = time.monotonic()
                    session.lock.release()
            self.server.slots.release()

    def do_OPTIONS(self) -> None:
        self._json(405, {"error": "AI_SERVICE_METHOD_NOT_ALLOWED"}, {"Allow": "GET, POST"})

    do_PUT = do_OPTIONS
    do_PATCH = do_OPTIONS
    do_DELETE = do_OPTIONS


def create_server(host: str, port: int, *, token: str, assistant_factory: Callable[[], Any]) -> _Server:
    """Create a loopback-only HTTP server. Externally reachable binds are rejected."""
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError("AI_SERVICE_BIND_INVALID") from exc
    if address.version != 4 or not address.is_loopback:
        raise ValueError("AI_SERVICE_BIND_MUST_BE_LOOPBACK")
    if isinstance(port, bool) or not isinstance(port, int) or not 0 <= port <= 65535:
        raise ValueError("AI_SERVICE_PORT_INVALID")
    if not isinstance(token, str) or len(token.encode("utf-8")) < 32:
        raise ValueError("AI_SERVICE_TOKEN_REQUIRED")
    if not callable(assistant_factory):
        raise ValueError("AI_SERVICE_FACTORY_INVALID")
    return _Server((str(address), port), token, assistant_factory)


def main() -> int:
    token = os.environ.get("PUSINGCUK_AI_SERVICE_TOKEN", "")
    if len(token.encode("utf-8")) < 32:
        print("PusingCuk AI service belum siap: AI_SERVICE_TOKEN_REQUIRED")
        return 2
    host = os.environ.get("PUSINGCUK_AI_SERVICE_BIND", "127.0.0.1")
    raw_port = os.environ.get("PUSINGCUK_AI_SERVICE_PORT", "8765")
    try:
        if not raw_port.isascii() or not raw_port.isdecimal():
            raise ValueError("AI_SERVICE_PORT_INVALID")
        port = int(raw_port)
        if not 1 <= port <= 65535:
            raise ValueError("AI_SERVICE_PORT_INVALID")
        index_path = Path(os.environ.get("PUSINGCUK_AI_INDEX", str(Path(__file__).with_name("knowledge_index.json"))))
        documents = load_index(index_path)
        provider_name = os.environ.get("PUSINGCUK_AI_PROVIDER", "ollama")
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
            raise ValueError("AI_SERVICE_PROVIDER_INVALID")
        server = create_server(
            host, port, token=token,
            assistant_factory=lambda: PusingCukAssistant(provider, documents),
        )
    except (OSError, ValueError, LocalAIProviderError) as exc:
        print(f"PusingCuk AI service belum siap: {getattr(exc, 'code', str(exc))}")
        return 2

    print(f"PusingCuk AI local service aktif: http://{host}:{port} (health /healthz, chat /v1/chat)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPusingCuk AI service dihentikan.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
