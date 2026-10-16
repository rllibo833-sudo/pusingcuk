"""Localhost-only web bridge for PusingCuk Studio (HTML + real runtime + PusingCuk AI)."""
from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
MAX_BODY = 4096
MAX_SOURCE = 20_000
MAX_STDIN = 4_000
TIMEOUT_SECONDS = 8


def _assistant():
    from library.assistant import PusingCukAssistant
    from library.knowledge_grounding import load_index
    from library.local_ai_provider import OllamaChatProvider
    model = os.environ.get("PUSINGCUK_AI_MODEL", "qwen3:4b")
    endpoint = os.environ.get("PUSINGCUK_OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat")
    return PusingCukAssistant(OllamaChatProvider(model=model, endpoint=endpoint),
                              load_index(ROOT / "library" / "knowledge_index.json"))


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class _Handler(BaseHTTPRequestHandler):
    server_version = "PusingCukStudioLocal"
    sys_version = ""

    def log_message(self, _format, *_args):
        return

    def reply(self, status, payload, content_type="application/json; charset=utf-8"):
        body = payload if isinstance(payload, bytes) else json.dumps(
            payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/", "/index.html"):
            try:
                self.reply(200, (WEB / "index.html").read_bytes(), "text/html; charset=utf-8")
            except OSError:
                self.reply(500, {"error": "STUDIO_HTML_MISSING"})
        elif path in ("/health", "/healthz"):
            self.reply(200, {"ok": True, "runtime": "python-reference", "ai": "ollama-configured"})
        else:
            self.reply(404, {"error": "ROUTE_NOT_FOUND"})

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/api/run", "/api/chat"):
            self.reply(404, {"error": "ROUTE_NOT_FOUND"})
            return
        if self.headers.get_content_type() != "application/json":
            self.reply(415, {"error": "JSON_REQUIRED"})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
            if not 0 <= length <= MAX_BODY:
                raise ValueError
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, UnicodeError, json.JSONDecodeError):
            self.reply(400, {"error": "REQUEST_INVALID"})
            return

        if path == "/api/chat":
            query = data.get("query")
            if not isinstance(query, str) or not query.strip() or len(query) > 300:
                self.reply(400, {"error": "QUERY_INVALID"})
                return
            try:
                assistant = _assistant()
                answer = assistant.ask(query)
                self.reply(200, {"ok": True, "answer": answer})
            except Exception as exc:
                # Return stable error classes, never local paths, tokens, or provider internals.
                code = getattr(exc, "code", "AI_PROVIDER_UNAVAILABLE")
                self.reply(503, {"ok": False, "error": str(code)[:80]})
            return

        source, stdin = data.get("source"), data.get("stdin", "")
        if not isinstance(source, str) or not source.strip() or len(source) > MAX_SOURCE:
            self.reply(400, {"error": "SOURCE_INVALID"})
            return
        if not isinstance(stdin, str) or len(stdin) > MAX_STDIN:
            self.reply(400, {"error": "STDIN_INVALID"})
            return
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".cuk",
                                             prefix=".studio-", dir=ROOT, delete=False) as f:
                f.write(source)
                temp_path = Path(f.name)
            result = subprocess.run(
                [sys.executable, str(ROOT / "pusingcuk_new.py"), str(temp_path)],
                cwd=ROOT, input=stdin, text=True, capture_output=True,
                timeout=TIMEOUT_SECONDS, check=False, shell=False,
            )
            self.reply(200, {"ok": result.returncode == 0, "stdout": result.stdout[-12000:],
                             "stderr": result.stderr[-6000:], "exit_code": result.returncode,
                             "timed_out": False})
        except subprocess.TimeoutExpired as exc:
            self.reply(200, {"ok": False, "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
                             "stderr": "Program melewati batas waktu 8 detik.",
                             "exit_code": None, "timed_out": True})
        except OSError:
            self.reply(503, {"error": "RUNTIME_UNAVAILABLE"})
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass


def main():
    host = os.environ.get("PUSINGCUK_STUDIO_BIND", "127.0.0.1")
    if host not in ("127.0.0.1", "localhost", "::1"):
        print("Studio hanya boleh bind ke localhost.")
        return 2
    try:
        port = int(os.environ.get("PUSINGCUK_STUDIO_PORT", "8765"))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        print("Port Studio tidak valid.")
        return 2
    server = _Server((host, port), _Handler)
    print(f"PusingCuk Studio lokal: http://127.0.0.1:{port}")
    print("Runtime bukan sandbox; jalankan hanya kode yang kamu percaya.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
