#!/usr/bin/env python3
"""Loopback-only HTML workbench that executes the compiled native Pusingcuk runtime."""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "web" / "index.html"
MAX_SOURCE_BYTES = 64 * 1024
MAX_REQUEST_BYTES = 96 * 1024
RUN_TIMEOUT_SECONDS = 3

def validate_payload(payload: object) -> tuple[str, str]:
    if not isinstance(payload, dict):
        raise ValueError("Permintaan harus berupa objek JSON.")
    source = payload.get("source")
    stdin = payload.get("stdin", "")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Kode Pusingcuk tidak boleh kosong.")
    if "\x00" in source:
        raise ValueError("Kode mengandung karakter NUL yang tidak diizinkan.")
    if not isinstance(stdin, str):
        raise ValueError("Input program harus berupa teks.")
    try:
        source_size = len(source.encode("utf-8"))
        stdin_size = len(stdin.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise ValueError("Kode atau input mengandung teks Unicode yang tidak valid.") from exc
    if source_size > MAX_SOURCE_BYTES:
        raise ValueError("Kode terlalu besar (maksimum 64 KiB).")
    if stdin_size > 16 * 1024:
        raise ValueError("Input program terlalu besar (maksimum 16 KiB).")
    return source, stdin

def build_native(tempdir: str) -> Path:
    compiler = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
    if not compiler:
        raise RuntimeError("Compiler C tidak ditemukan. Pasang clang atau gcc terlebih dahulu.")
    binary = Path(tempdir) / "pusingcuk-native"
    result = subprocess.run(
        [compiler, "-std=c11", "-O2", "-Wall", "-Wextra",
         str(ROOT / "native" / "pusingcuk.c"), "-lm", "-o", str(binary)],
        cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
    )
    if result.returncode:
        details = (result.stderr or result.stdout or "kesalahan compiler")[-4000:]
        raise RuntimeError("Build runtime native gagal:\n" + details)
    return binary

def run_program(binary: Path, source: str, stdin: str = "") -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="pusingcuk-run-") as workdir:
        program = Path(workdir) / "program.pusingcuk"
        program.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(
                [str(binary), str(program)], input=stdin, capture_output=True,
                text=True, encoding="utf-8", errors="replace", cwd=workdir,
                timeout=RUN_TIMEOUT_SECONDS, check=False,
                env={"PATH": os.environ.get("PATH", ""), "LC_ALL": "C.UTF-8"},
            )
            return {"ok": result.returncode == 0, "exit_code": result.returncode,
                    "stdout": result.stdout[-20000:], "stderr": result.stderr[-8000:],
                    "timed_out": False}
        except subprocess.TimeoutExpired as exc:
            out, err = exc.stdout or "", exc.stderr or ""
            if isinstance(out, bytes): out = out.decode("utf-8", "replace")
            if isinstance(err, bytes): err = err.decode("utf-8", "replace")
            return {"ok": False, "exit_code": None, "stdout": out[-20000:],
                    "stderr": (err + "\nEksekusi dihentikan setelah batas waktu 3 detik.")[-8000:],
                    "timed_out": True}

class WorkbenchServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def make_handler(binary: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = "PusingcukWorkbench/1.0"
        def log_message(self, _format, *_args):
            return
        def send_bytes(self, status: int, data: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def send_json(self, status: int, value: dict[str, object]):
            self.send_bytes(status, json.dumps(value, ensure_ascii=False).encode("utf-8"),
                            "application/json; charset=utf-8")
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/":
                try: data = HTML_FILE.read_bytes()
                except OSError:
                    self.send_json(500, {"error": "File web/index.html tidak ditemukan."})
                    return
                self.send_bytes(200, data, "text/html; charset=utf-8")
            elif path == "/health":
                self.send_json(200, {"ok": True, "runtime": "native-c"})
            else:
                self.send_json(404, {"error": "Rute tidak ditemukan."})
        def do_POST(self):
            if urlsplit(self.path).path != "/api/run":
                self.send_json(404, {"error": "Rute tidak ditemukan."})
                return
            origin = self.headers.get("Origin")
            allowed = {f"http://127.0.0.1:{self.server.server_port}",
                       f"http://localhost:{self.server.server_port}"}
            if origin and origin not in allowed:
                self.send_json(403, {"error": "Origin tidak diizinkan."})
                return
            media_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if media_type != "application/json":
                self.send_json(415, {"error": "Gunakan Content-Type application/json."})
                return
            try: length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.send_json(400, {"error": "Content-Length tidak valid."})
                return
            if length <= 0 or length > MAX_REQUEST_BYTES:
                self.send_json(413, {"error": "Ukuran permintaan tidak valid atau terlalu besar."})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                source, stdin = validate_payload(payload)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                self.send_json(400, {"error": str(exc)})
                return
            self.send_json(200, run_program(binary, source, stdin))
    return Handler

def main() -> int:
    with tempfile.TemporaryDirectory(prefix="pusingcuk-workbench-") as builddir:
        try: binary = build_native(builddir)
        except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
            import sys
            print(f"Workbench tidak dapat dimulai: {exc}", file=sys.stderr)
            return 2
        server = WorkbenchServer(("127.0.0.1", 8765), make_handler(binary))
        print("Pusingcuk Studio lokal: http://127.0.0.1:8765")
        print("Hanya menerima koneksi dari perangkat ini. Tekan Ctrl+C untuk berhenti.")
        try: server.serve_forever()
        except KeyboardInterrupt: print("\nPusingcuk Studio dihentikan.")
        finally: server.server_close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
