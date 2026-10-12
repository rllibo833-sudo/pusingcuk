"""Loopback-only JSON HTTP server for local development and offline tests."""
from __future__ import annotations

import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit


class ServerAdapterError(RuntimeError):
    """Local server configuration or request failure."""


class LocalHTTPServer:
    """Explicit JSON routes bound to a loopback IP only; not a production server."""

    def __init__(self, routes=None, *, host="127.0.0.1", port=0,
                 max_body_bytes=1_048_576):
        try:
            if not ipaddress.ip_address(host).is_loopback:
                raise ServerAdapterError("server hanya boleh bind ke alamat loopback")
        except ValueError as exc:
            raise ServerAdapterError("host harus berupa IP loopback literal") from exc
        if not isinstance(port, int) or isinstance(port, bool) or not 0 <= port <= 65535:
            raise ServerAdapterError("port harus antara 0 dan 65535")
        if not isinstance(max_body_bytes, int) or not 1 <= max_body_bytes <= 8_388_608:
            raise ServerAdapterError("batas body harus antara 1 byte dan 8 MiB")
        self.host, self.port = host, port
        self.max_body_bytes = max_body_bytes
        self.routes = {}
        for key, handler in (routes or {}).items():
            if not isinstance(key, tuple) or len(key) != 2:
                raise ServerAdapterError("route harus memakai kunci (METHOD, /path)")
            self.add_route(key[0], key[1], handler)
        self._server = None
        self._thread = None

    def add_route(self, method, path, handler):
        method = str(method).upper()
        if method not in {"GET", "POST", "PUT", "DELETE"}:
            raise ServerAdapterError("metode HTTP tidak didukung")
        if not isinstance(path, str) or not path.startswith("/") or "?" in path or "#" in path:
            raise ServerAdapterError("path route harus berupa path absolut tanpa query")
        if not callable(handler):
            raise ServerAdapterError("handler route harus berupa fungsi")
        self.routes[(method, path)] = handler

    def _make_server(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, _format, *args):
                return

            def _send(self, status, value):
                try:
                    body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
                except (TypeError, ValueError):
                    status, body = 500, b'{"error":"response tidak valid"}'
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(body)

            def _dispatch(self):
                path = urlsplit(self.path).path
                handler = owner.routes.get((self.command, path))
                if handler is None:
                    self._send(404, {"error": "route tidak ditemukan"})
                    return
                payload = None
                if self.command in {"POST", "PUT", "DELETE"}:
                    raw_length = self.headers.get("Content-Length", "0")
                    try:
                        length = int(raw_length)
                    except ValueError:
                        self._send(400, {"error": "Content-Length tidak valid"})
                        return
                    if length < 0 or length > owner.max_body_bytes:
                        self._send(413, {"error": "body terlalu besar"})
                        return
                    raw = self.rfile.read(length)
                    if len(raw) != length:
                        self._send(400, {"error": "body tidak lengkap"})
                        return
                    if raw:
                        try:
                            payload = json.loads(raw.decode("utf-8"))
                        except (UnicodeDecodeError, json.JSONDecodeError):
                            self._send(400, {"error": "body harus JSON UTF-8 yang valid"})
                            return
                try:
                    result = handler(payload, dict(self.headers.items()))
                    status, value = result if (
                        isinstance(result, tuple) and len(result) == 2
                        and isinstance(result[0], int)
                    ) else (200, result)
                    if not 100 <= status <= 599:
                        raise ValueError("status HTTP tidak valid")
                    self._send(status, value)
                except Exception:
                    # Never leak exception text or traceback to HTTP clients.
                    self._send(500, {"error": "kesalahan internal"})

            do_GET = _dispatch
            do_POST = _dispatch
            do_PUT = _dispatch
            do_DELETE = _dispatch

        try:
            return ThreadingHTTPServer((self.host, self.port), Handler)
        except OSError as exc:
            raise ServerAdapterError(f"gagal memulai server lokal: {exc}") from exc

    @property
    def address(self):
        if self._server is None:
            return (self.host, self.port)
        return self._server.server_address

    def start(self):
        if self._server is not None:
            raise ServerAdapterError("server sudah berjalan")
        self._server = self._make_server()
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def close(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc, tb):
        self.close()
