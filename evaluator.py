"""Evaluator terpisah untuk AST dari parser.py."""
from contextlib import redirect_stdout
from collections.abc import MutableMapping
from io import StringIO
from pathlib import Path
from urllib.request import Request
from urllib.parse import urlsplit, urljoin
import http.client
import ipaddress
import os
import socket
import ssl
import stat
import json
from pathlib import Path, PureWindowsPath
from datetime import datetime, date
from ast_nodes import Node
from parser import parse
from library.stdlib import BUILTINS, call_builtin


class PusingDict(MutableMapping):
    """Language dictionary: booleans are distinct from numeric keys, unlike Python dict."""
    def __init__(self):
        self._entries = []

    @staticmethod
    def _supported(key):
        return isinstance(key, (str, int, float, bool))

    def _index(self, key):
        if not self._supported(key):
            raise TypeError("kunci kamus harus berupa teks, angka, atau boolean")
        for index, (existing, _value) in enumerate(self._entries):
            if isinstance(existing, bool) or isinstance(key, bool):
                same = type(existing) is type(key) and existing == key
            elif isinstance(existing, (int, float)) and isinstance(key, (int, float)):
                same = existing == key
            else:
                same = type(existing) is type(key) and existing == key
            if same:
                return index
        return -1

    def __getitem__(self, key):
        index = self._index(key)
        if index < 0:
            raise KeyError(key)
        return self._entries[index][1]

    def __setitem__(self, key, value):
        index = self._index(key)
        if index < 0:
            self._entries.append((key, value))
        else:
            self._entries[index] = (self._entries[index][0], value)

    def __delitem__(self, key):
        index = self._index(key)
        if index < 0:
            raise KeyError(key)
        del self._entries[index]

    def __iter__(self):
        return (key for key, _value in self._entries)

    def __len__(self):
        return len(self._entries)

    def __repr__(self):
        return "{" + ", ".join(f"{key!r}: {value!r}" for key, value in self._entries) + "}"


def language_equal(left, right):
    # In Pusingcuk, boolean and numeric values are different types.
    if isinstance(left, bool) != isinstance(right, bool):
        if isinstance(left, (bool, int, float)) and isinstance(right, (bool, int, float)):
            return False
    return left == right


def _json_ready(value):
    """Convert Pusingcuk collections into values accepted by json."""
    if isinstance(value, PusingDict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError("nilai tidak didukung oleh JSON")


def _language_json(value):
    """Convert decoded JSON objects into Pusingcuk dictionaries recursively."""
    if isinstance(value, dict):
        result = PusingDict()
        for key, item in value.items():
            result[key] = _language_json(item)
        return result
    if isinstance(value, list):
        return [_language_json(item) for item in value]
    return value

class ExportedFunction:
    def __init__(self, evaluator, name, module_env):
        self.evaluator = evaluator
        self.name = name
        self.module_env = module_env


class ReturnSignal(BaseException):
    """Internal control-flow signal; runtime try/catch must never swallow returns."""
    def __init__(self, value):
        self.value = value


MAX_HTTP_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_HTTP_REQUEST_BYTES = 1 * 1024 * 1024


# Reject local/private redirect destinations before urllib follows them.
_BLOCKED_NETWORKS = tuple(
    ipaddress.ip_network(network)
    for network in (
        "0.0.0.0/32", "10.0.0.0/8", "127.0.0.0/8",
        "169.254.0.0/16", "172.16.0.0/12", "192.168.0.0/16",
        "::1/128", "fc00::/7", "fe80::/10",
    )
)


def _is_blocked_address(address):
    """Reject non-public destinations, including IPv4-mapped IPv6 addresses."""
    if getattr(address, "ipv4_mapped", None) is not None:
        address = address.ipv4_mapped
    return not address.is_global or any(
        address.version == network.version and address in network
        for network in _BLOCKED_NETWORKS
    )


def _is_blocked_hostname(hostname):
    """Fail closed if any DNS answer is non-public."""
    host = hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        literal = ipaddress.ip_address(host.split("%", 1)[0])
    except ValueError:
        try:
            results = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
            if not results:
                return True
            addresses = [ipaddress.ip_address(result[4][0].split("%", 1)[0]) for result in results]
        except (OSError, ValueError):
            return True
        return any(_is_blocked_address(address) for address in addresses)
    return _is_blocked_address(literal)


def _valid_http_url(url):
    """Accept HTTP(S) URLs only when their host is not a local/private address."""
    try:
        parsed = urlsplit(url)
        return (
            parsed.scheme.lower() in ("http", "https")
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not _is_blocked_hostname(parsed.hostname)
        )
    except (TypeError, ValueError):
        return False


def _resolve_public_address(hostname, port):
    """Resolve once, validate every answer and return a numeric socket address."""
    host = hostname.split("%", 1)[0]
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        try:
            results = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ValueError("DNS tidak dapat diresolusikan") from exc
        if not results:
            raise ValueError("DNS tidak memiliki alamat")
        candidates = []
        for family, _socktype, _proto, _canonname, sockaddr in results:
            address = ipaddress.ip_address(sockaddr[0].split("%", 1)[0])
            if _is_blocked_address(address):
                raise ValueError("tujuan HTTP non-publik diblokir")
            if family in (socket.AF_INET, socket.AF_INET6):
                sockaddr = (sockaddr[0], port, *sockaddr[2:]) if family == socket.AF_INET6 else (sockaddr[0], port)
                candidates.append((family, sockaddr))
        if not candidates:
            raise ValueError("DNS tidak memiliki alamat yang didukung")
        return candidates[0]
    if _is_blocked_address(literal):
        raise ValueError("tujuan HTTP non-publik diblokir")
    family = socket.AF_INET6 if literal.version == 6 else socket.AF_INET
    sockaddr = (str(literal), port, 0, 0) if family == socket.AF_INET6 else (str(literal), port)
    return family, sockaddr


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host, port, family, sockaddr, timeout):
        super().__init__(host, port, timeout=timeout)
        self._pinned_family, self._pinned_sockaddr = family, sockaddr

    def connect(self):
        sock = socket.socket(self._pinned_family, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect(self._pinned_sockaddr)
        except Exception:
            sock.close()
            raise
        self.sock = sock


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, port, family, sockaddr, timeout):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self._pinned_family, self._pinned_sockaddr = family, sockaddr

    def connect(self):
        sock = socket.socket(self._pinned_family, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect(self._pinned_sockaddr)
            self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
        except Exception:
            sock.close()
            raise


class _PinnedResponse:
    """Keep the validated connection alive while reading its bounded response."""
    def __init__(self, response, connection, url):
        self._response, self._connection, self._url = response, connection, url
        self.headers = response.headers

    def read(self, size=-1):
        return self._response.read(size)

    def geturl(self):
        return self._url

    def close(self):
        try:
            self._response.close()
        finally:
            self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
        return False


def urlopen(request, timeout=10):
    """Connect directly to a validated numeric IP, never re-resolving for TCP."""
    current_url = request.full_url
    method, body = request.get_method().upper(), request.data
    headers = dict(request.header_items())
    for redirect_count in range(4):
        parsed = urlsplit(current_url)
        scheme, hostname = parsed.scheme.lower(), parsed.hostname
        if scheme not in ("http", "https") or not hostname or parsed.username is not None:
            raise ValueError("URL HTTP(S) tidak valid")
        port = parsed.port or (443 if scheme == "https" else 80)
        family, sockaddr = _resolve_public_address(hostname, port)
        connection = (
            _PinnedHTTPSConnection(hostname, port, family, sockaddr, timeout)
            if scheme == "https" else
            _PinnedHTTPConnection(hostname, port, family, sockaddr, timeout)
        )
        target = parsed.path or "/"
        if parsed.query:
            target += "?" + parsed.query
        try:
            connection.request(method, target, body=body, headers=headers)
            response = connection.getresponse()
        except Exception:
            connection.close()
            raise
        status, location = response.status, response.getheader("Location")
        if status in (301, 302, 303, 307, 308) and location:
            response.close()
            connection.close()
            if redirect_count >= 3:
                raise ValueError("terlalu banyak redirect HTTP")
            current_url = urljoin(current_url, location)
            if status == 303 or (status in (301, 302) and method not in ("GET", "HEAD")):
                method, body = "GET", None
                headers = {key: value for key, value in headers.items() if key.lower() not in ("content-type", "content-length", "host")}
            continue
        return _PinnedResponse(response, connection, current_url)
    raise ValueError("terlalu banyak redirect HTTP")


def _response_url_is_safe(response, original_url):
    """Check the final URL as a second guard after the redirect chain."""
    try:
        final_url = response.geturl()
    except AttributeError:
        final_url = original_url
    return _valid_http_url(final_url)


def _read_http_response(response):
    """Read at most the configured response limit plus one sentinel byte."""
    data = response.read(MAX_HTTP_RESPONSE_BYTES + 1)
    if len(data) > MAX_HTTP_RESPONSE_BYTES:
        return False
    charset = response.headers.get_content_charset() or "utf-8"
    return data.decode(charset, errors="replace")


MAX_MODULE_FILE_BYTES = 1 * 1024 * 1024
MAX_MODULE_DEPTH = 20
_REPO_ROOT = Path(__file__).resolve().parent


def _project_path_parts(project_root, raw_path, base_dir=None):
    if not isinstance(raw_path, (str, Path)) or not str(raw_path):
        raise ValueError("path harus berupa teks relatif non-kosong")
    raw_text = str(raw_path)
    lexical, windows = Path(raw_text), PureWindowsPath(raw_text)
    if lexical.is_absolute() or windows.is_absolute() or windows.drive:
        raise ValueError("path absolut tidak diizinkan")
    if ".." in raw_text.replace("\\", "/").split("/"):
        raise ValueError("path traversal tidak diizinkan")
    root = Path(project_root).resolve()
    base = Path(base_dir or root).resolve()
    try:
        base_parts = base.relative_to(root).parts
    except ValueError as exc:
        raise ValueError("direktori dasar berada di luar project root") from exc
    parts = tuple(base_parts) + tuple(part for part in lexical.parts if part not in ("", "."))
    if not parts:
        raise ValueError("path harus menunjuk ke berkas di dalam project root")
    return root, parts


def _confined_project_path(project_root, raw_path, base_dir=None):
    root, parts = _project_path_parts(project_root, raw_path, base_dir)
    candidate = root
    for part in parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("symlink tidak diizinkan untuk operasi berkas")
        candidate = candidate.resolve(strict=False)
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("path keluar dari project root") from exc
    if candidate == root:
        raise ValueError("operasi berkas tidak boleh menunjuk ke project root")
    return candidate


def _open_project_file(project_root, raw_path, flags, mode=0o666, base_dir=None):
    root, parts = _project_path_parts(project_root, raw_path, base_dir)
    nofollow, directory_flag = getattr(os, "O_NOFOLLOW", 0), getattr(os, "O_DIRECTORY", 0)
    if nofollow and directory_flag and os.open in getattr(os, "supports_dir_fd", set()):
        root_fd = os.open(root, os.O_RDONLY | directory_flag)
        opened_dirs, current_fd = [], root_fd
        try:
            for part in parts[:-1]:
                next_fd = os.open(part, os.O_RDONLY | directory_flag | nofollow, dir_fd=current_fd)
                opened_dirs.append(next_fd)
                current_fd = next_fd
            fd = os.open(parts[-1], flags | nofollow, mode, dir_fd=current_fd)
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                os.close(fd)
                raise ValueError("hanya berkas reguler yang diizinkan")
            return fd
        finally:
            for directory_fd in reversed(opened_dirs):
                os.close(directory_fd)
            os.close(root_fd)
    path = _confined_project_path(root, raw_path, base_dir)
    fd = os.open(path, flags | nofollow, mode)
    try:
        Path(os.path.realpath(path)).relative_to(root)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("hanya berkas reguler yang diizinkan")
        return fd
    except Exception:
        os.close(fd)
        raise


def _read_project_text(project_root, raw_path, base_dir=None, max_bytes=None):
    fd = _open_project_file(project_root, raw_path, os.O_RDONLY, base_dir=base_dir)
    with os.fdopen(fd, "rb") as stream:
        data = stream.read(max_bytes + 1 if max_bytes is not None else -1)
    if max_bytes is not None and len(data) > max_bytes:
        raise ValueError("berkas melebihi batas ukuran")
    return data.decode("utf-8")


def _write_project_text(project_root, raw_path, text, base_dir=None):
    fd = _open_project_file(project_root, raw_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, base_dir=base_dir)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)


def _delete_project_file(project_root, raw_path):
    root, parts = _project_path_parts(project_root, raw_path)
    nofollow, directory_flag = getattr(os, "O_NOFOLLOW", 0), getattr(os, "O_DIRECTORY", 0)
    if not (nofollow and directory_flag and os.open in getattr(os, "supports_dir_fd", set())):
        _confined_project_path(root, raw_path).unlink()
        return
    root_fd = os.open(root, os.O_RDONLY | directory_flag)
    opened_dirs, current_fd = [], root_fd
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | directory_flag | nofollow, dir_fd=current_fd)
            opened_dirs.append(next_fd)
            current_fd = next_fd
        entry_stat = os.stat(parts[-1], dir_fd=current_fd, follow_symlinks=False)
        if stat.S_ISLNK(entry_stat.st_mode):
            raise ValueError("symlink tidak diizinkan untuk operasi berkas")
        os.unlink(parts[-1], dir_fd=current_fd)
    finally:
        for directory_fd in reversed(opened_dirs):
            os.close(directory_fd)
        os.close(root_fd)


class Evaluator:
    def __init__(self, source_path=None, project_root=None, module_cache=None,
                 module_loading_stack=None, module_depth=0, is_main=True):
        self.functions = {}
        self.budget = 0
        self.source_path = Path(source_path).resolve() if source_path is not None else None
        self.project_root = Path(project_root or _REPO_ROOT).resolve()
        self._module_cache = module_cache if module_cache is not None else {}
        self._module_loading_stack = (
            module_loading_stack if module_loading_stack is not None else set()
        )
        self._module_depth = module_depth
        self._is_main = is_main

    def fail(self, line, message):
        raise RuntimeError(f"Baris {line}: {message}")

    def step(self, line):
        self.budget += 1
        if self.budget > 100000:
            self.fail(line, "batas total 100000 langkah tercapai")

    def expr(self, n, env, depth=0):
        k, line = n.kind, n.line
        try:
            if k == "Literal":
                return n.value
            if k == "Variable":
                if n.name not in env:
                    self.fail(line, f"variabel '{n.name}' belum dibuat")
                return env[n.name]
            if k == "List":
                return [self.expr(x, env, depth) for x in n.items]
            if k == "Dict":
                result = PusingDict()
                for key_node, value_node in n.items:
                    key = self.expr(key_node, env, depth)
                    value = self.expr(value_node, env, depth)
                    try:
                        result[key] = value
                    except (TypeError, ValueError):
                        self.fail(key_node.line, "kunci kamus harus dapat digunakan sebagai kunci")
                return result
            if k == "Index":
                obj = self.expr(n.collection, env, depth)
                idx = self.expr(n.index, env, depth)
                if isinstance(obj, (list, str)):
                    if not isinstance(idx, int) or isinstance(idx, bool):
                        self.fail(line, "indeks harus berupa bilangan bulat")
                    if idx < 0 or idx >= len(obj):
                        self.fail(line, "indeks di luar batas")
                    return obj[idx]
                if isinstance(obj, PusingDict):
                    try:
                        return obj[idx]
                    except (KeyError, TypeError):
                        self.fail(line, "kunci kamus tidak ditemukan")
                self.fail(line, "indeks hanya dapat digunakan pada daftar, teks, atau kamus")
            if k == "Unary":
                v = self.expr(n.value, env, depth)
                if n.op == "bukan":
                    return not v
                if n.op == "-":
                    return -v
                self.fail(line, "operator unary tidak dikenal")
            if k == "Binary":
                a = self.expr(n.left, env, depth)
                if n.op == "dan":
                    return bool(a) and bool(self.expr(n.right, env, depth))
                if n.op == "atau":
                    return bool(a) or bool(self.expr(n.right, env, depth))
                b = self.expr(n.right, env, depth)
                ops = {
                    "+": lambda: a + b, "-": lambda: a - b,
                    "*": lambda: a * b, "/": lambda: a / b,
                    "//": lambda: a // b, "%": lambda: a % b,
                    "==": lambda: language_equal(a, b), "!=": lambda: not language_equal(a, b),
                    "<": lambda: a < b, "<=": lambda: a <= b,
                    ">": lambda: a > b, ">=": lambda: a >= b,
                }
                if n.op not in ops:
                    self.fail(line, "operator tidak dikenal")
                if n.op == "+":
                    numeric = (isinstance(a, (int, float)) and not isinstance(a, bool)
                               and isinstance(b, (int, float)) and not isinstance(b, bool))
                    same_text = isinstance(a, str) and isinstance(b, str)
                    same_list = isinstance(a, list) and isinstance(b, list)
                    if not (numeric or same_text or same_list):
                        self.fail(line, "operator '+' membutuhkan dua angka, dua teks, atau dua daftar; ubah angka menjadi teks secara eksplisit jika ingin menggabungkan teks")
                return ops[n.op]()
            if k == "Call":
                args = [self.expr(x, env, depth) for x in n.args]
                if n.name in ("jam", "tanggal"):
                    if args:
                        self.fail(line, f"fungsi '{n.name}' tidak membutuhkan argumen")
                    if n.name == "jam":
                        return datetime.now().astimezone().isoformat(timespec="seconds")
                    return date.today().isoformat()
                if n.name == "angkut":
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, "angkut membutuhkan satu path berkas teks")
                    raw_path = Path(args[0])
                    if raw_path.suffix not in {".cuk", ".pusingcuk"}:
                        return False
                    if self._module_depth >= MAX_MODULE_DEPTH:
                        return False
                    # Module paths are relative to the entrypoint's directory (or the importing module's directory).
                    base_dir = self.source_path.parent if self.source_path is not None else self.project_root
                    try:
                        path = _confined_project_path(self.project_root, args[0], base_dir)
                        if not path.is_file() or path.stat().st_size > MAX_MODULE_FILE_BYTES:
                            return False
                        source = _read_project_text(self.project_root, args[0], base_dir, max_bytes=MAX_MODULE_FILE_BYTES)
                    except (OSError, UnicodeError, ValueError):
                        return False

                    if path in self._module_loading_stack:
                        # A cycle is a failed import, not unbounded recursive evaluation.
                        return False
                    if path in self._module_cache:
                        return self._module_cache[path]
                    try:
                        if not path.is_file() or path.stat().st_size > MAX_MODULE_FILE_BYTES:
                            return False
                        source = path.read_text(encoding="utf-8")
                    except (OSError, UnicodeError):
                        return False

                    self._module_loading_stack.add(path)
                    try:
                        module_evaluator = Evaluator(
                            source_path=path,
                            project_root=self.project_root,
                            module_cache=self._module_cache,
                            module_loading_stack=self._module_loading_stack,
                            module_depth=self._module_depth + 1,
                            is_main=False,
                        )
                        module_env = module_evaluator.run_module(source)
                        exports = PusingDict()
                        for key, value in module_env.items():
                            exports[key] = value
                        for key in module_evaluator.functions:
                            exports[key] = ExportedFunction(module_evaluator, key, module_env)
                        self._module_cache[path] = exports
                        return exports
                    finally:
                        self._module_loading_stack.discard(path)
                if "." in n.name:
                    module_name, function_name = n.name.split(".", 1)
                    module = env.get(module_name)
                    if not isinstance(module, PusingDict):
                        self.fail(line, f"modul '{module_name}' tidak ditemukan")
                    try:
                        exported = module[function_name]
                    except KeyError:
                        self.fail(line, f"modul '{module_name}' tidak mengekspor '{function_name}'")
                    if not isinstance(exported, ExportedFunction):
                        self.fail(line, f"ekspor '{function_name}' bukan fungsi")
                    return exported.evaluator.call_export(exported.name, args, exported.module_env, depth, line)
                if n.name == "tanya":
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, "tanya membutuhkan satu prompt teks")
                    return input(args[0])
                if n.name == "tulis":
                    if len(args) != 2 or not all(isinstance(x, str) for x in args):
                        self.fail(line, "tulis membutuhkan path dan teks berupa string")
                    try:
                        _write_project_text(self.project_root, args[0], args[1])
                        return True
                    except (OSError, ValueError):
                        return False
                if n.name == "baca":
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, "baca membutuhkan satu path berupa string")
                    try:
                        return _read_project_text(self.project_root, args[0])
                    except (OSError, ValueError, UnicodeError):
                        return False
                if n.name == "tulis_json":
                    if len(args) != 2 or not isinstance(args[0], str):
                        self.fail(line, "tulis_json membutuhkan path teks dan satu objek")
                    try:
                        data = _json_ready(args[1])
                        _write_project_text(self.project_root, args[0], json.dumps(data, ensure_ascii=False, indent=2))
                        return True
                    except (OSError, TypeError, ValueError):
                        return False
                if n.name == "baca_json":
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, "baca_json membutuhkan satu path berupa teks")
                    try:
                        data = json.loads(_read_project_text(self.project_root, args[0]))
                        return _language_json(data)
                    except (OSError, ValueError, UnicodeError):
                        return False
                if n.name == "kepo_internet":
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, "kepo_internet membutuhkan satu URL teks")
                    if not _valid_http_url(args[0]):
                        return False
                    try:
                        request = Request(args[0], headers={"User-Agent": "Pusingcuk/0.5 (Internet Native)"}, method="GET")
                        with urlopen(request, timeout=10) as response:
                            if not _response_url_is_safe(response, request.full_url):
                                return False
                            return _read_http_response(response)
                    except Exception:
                        return False
                if n.name == "kirim_api":
                    if len(args) != 2 or not isinstance(args[0], str):
                        self.fail(line, "kirim_api membutuhkan URL dan data")
                    if not _valid_http_url(args[0]):
                        return False
                    try:
                        payload = args[1]
                        if isinstance(payload, (dict, PusingDict)):
                            body = json.dumps(_json_ready(payload), ensure_ascii=False).encode("utf-8")
                            content_type = "application/json; charset=utf-8"
                        elif isinstance(payload, str):
                            body = payload.encode("utf-8")
                            content_type = "text/plain; charset=utf-8"
                        else:
                            return False
                        if len(body) > MAX_HTTP_REQUEST_BYTES:
                            return False
                        request = Request(args[0], data=body, headers={"User-Agent": "Pusingcuk/0.5 (Internet Native)", "Content-Type": content_type}, method="POST")
                        with urlopen(request, timeout=10) as response:
                            return _read_http_response(response)
                    except Exception:
                        return False
                if n.name == "jadi_json":
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, "jadi_json membutuhkan satu teks JSON")
                    try:
                        return _language_json(json.loads(args[0]))
                    except json.JSONDecodeError:
                        return False
                if n.name == "jadi_teks":
                    if len(args) != 1:
                        self.fail(line, "jadi_teks membutuhkan satu objek")
                    try:
                        return json.dumps(_json_ready(args[0]), ensure_ascii=False)
                    except (TypeError, ValueError):
                        return False
                if n.name == "warna":
                    if len(args) != 2:
                        self.fail(line, "warna membutuhkan teks dan nama warna")
                    colors = {"merah": "31", "hijau": "32", "kuning": "33", "biru": "34", "pink": "35", "sian": "36"}
                    if not isinstance(args[1], str) or args[1] not in colors:
                        self.fail(line, "warna tidak dikenal; pilih merah, hijau, kuning, biru, pink, atau sian")
                    return "\x1b[" + colors[args[1]] + "m" + str(args[0]) + "\x1b[0m"
                if n.name == "panjang":
                    if len(args) != 1:
                        self.fail(line, "fungsi 'panjang' membutuhkan 1 argumen")
                    if not isinstance(args[0], (list, str, PusingDict, range)):
                        self.fail(line, "panjang menerima daftar, teks, kamus, atau rentang")
                    return len(args[0])
                if n.name == "rentang":
                    if not 1 <= len(args) <= 3:
                        self.fail(line, "fungsi 'rentang' membutuhkan 1 sampai 3 argumen")
                    if any(not isinstance(x, int) or isinstance(x, bool) for x in args):
                        self.fail(line, "argumen rentang harus bilangan bulat")
                    try:
                        return range(*args)
                    except ValueError:
                        self.fail(line, "langkah rentang tidak boleh nol")
                if n.name in BUILTINS:
                    try:
                        return call_builtin(n.name, *args)
                    except (TypeError, ValueError, OverflowError) as exc:
                        self.fail(line, str(exc))
                if n.name not in self.functions:
                    self.fail(line, f"fungsi '{n.name}' tidak dikenal")
                params, body, fline = self.functions[n.name]
                if len(args) != len(params):
                    self.fail(line, f"fungsi '{n.name}' membutuhkan {len(params)} argumen")
                if depth >= 100:
                    self.fail(line, "batas kedalaman pemanggilan fungsi tercapai")
                local = dict(zip(params, args))
                try:
                    self.block(body, local, depth + 1, True)
                except ReturnSignal as ret:
                    return ret.value
                return None
            self.fail(line, f"ekspresi '{k}' belum didukung")
        except RuntimeError:
            raise
        except Exception as exc:
            self.fail(line, f"operasi gagal ({type(exc).__name__})")

    def call_export(self, name, args, module_env, depth, line):
        params, body, _fline = self.functions[name]
        if len(args) != len(params):
            self.fail(line, f"fungsi '{name}' membutuhkan {len(params)} argumen")
        if depth >= 100:
            self.fail(line, "batas kedalaman pemanggilan fungsi tercapai")
        local = dict(module_env)
        local.update(zip(params, args))
        try:
            self.block(body, local, depth + 1, True)
        except ReturnSignal as ret:
            return ret.value
        return None

    def assign_index(self, target, value, env, line, depth):
        if target.kind == "Variable":
            if target.name not in env:
                self.fail(line, f"variabel '{target.name}' belum dibuat")
            obj = env[target.name]
        elif target.kind == "Index":
            obj = self.expr(target, env, depth)
        else:
            self.fail(line, "target indeks tidak valid")
        if not isinstance(obj, (list, PusingDict)):
            self.fail(line, "assignment indeks hanya mendukung daftar atau kamus")
        return obj

    def block(self, body, env, depth=0, in_function=False):
        for n in body:
            line, k = n.line, n.kind
            self.step(line)
            if k == "Call":
                self.expr(n, env, depth)
            elif k == "Declare":
                if n.name in env:
                    self.fail(line, f"variabel '{n.name}' sudah dibuat")
                env[n.name] = self.expr(n.value, env, depth)
            elif k == "Assign":
                if n.name not in env:
                    self.fail(line, f"variabel '{n.name}' belum dibuat")
                env[n.name] = self.expr(n.value, env, depth)
            elif k == "IndexAssign":
                obj = self.assign_index(n.collection, None, env, line, depth)
                idx = self.expr(n.index, env, depth)
                value = self.expr(n.value, env, depth)
                if isinstance(obj, list):
                    if not isinstance(idx, int) or isinstance(idx, bool):
                        self.fail(line, "indeks harus berupa bilangan bulat")
                    if idx < 0 or idx >= len(obj):
                        self.fail(line, "indeks daftar di luar batas")
                    obj[idx] = value
                elif isinstance(obj, PusingDict):
                    try:
                        obj[idx] = value
                    except TypeError:
                        self.fail(line, "kunci kamus harus dapat digunakan sebagai kunci")
            elif k == "Input":
                if n.name in env:
                    self.fail(line, "variabel '" + n.name + "' sudah dibuat")
                prompt = self.expr(n.prompt, env, depth)
                if not isinstance(prompt, str):
                    self.fail(line, "prompt tanya harus berupa string")
                env[n.name] = input(prompt)
            elif k == "Print":
                value = self.expr(n.value, env, depth)
                if value is True:
                    value = "okelah"
                elif value is False:
                    value = "tidak"
                print(value)
            elif k == "Try":
                try:
                    self.block(n.body, env, depth, in_function)
                except ReturnSignal:
                    raise
                except Exception as exc:
                    if n.handler_name is None:
                        raise
                    catch_env = dict(env)
                    catch_env[n.handler_name] = str(exc)
                    self.block(n.handler, catch_env, depth, in_function)
                    env.update({key: value for key, value in catch_env.items() if key != n.handler_name})
                finally:
                    self.block(n.final, env, depth, in_function)
            elif k == "If":
                branch = n.then_body if self.expr(n.condition, env, depth) else n.else_body
                self.block(branch, env, depth, in_function)
            elif k == "While":
                count = 0
                while self.expr(n.condition, env, depth):
                    self.step(line)
                    if count >= 10000:
                        self.fail(line, "batas 10000 iterasi tercapai")
                    self.block(n.body, env, depth, in_function)
                    count += 1
            elif k == "For":
                iterable = self.expr(n.iterable, env, depth)
                if not isinstance(iterable, (list, tuple, str, PusingDict, range)):
                    self.fail(line, "untuk membutuhkan daftar, teks, kamus, atau rentang")
                count = 0
                for item in iterable:
                    self.step(line)
                    if count >= 10000:
                        self.fail(line, "batas 10000 iterasi tercapai")
                    env[n.name] = item
                    self.block(n.body, env, depth, in_function)
                    count += 1
            elif k == "Function":
                if n.name in ("panjang", "rentang"):
                    self.fail(line, f"nama fungsi '{n.name}' sudah digunakan")
                definition = (n.params, n.body, line)
                if n.name in self.functions:
                    if self.functions[n.name] != definition:
                        self.fail(line, f"fungsi '{n.name}' sudah dibuat")
                else:
                    self.functions[n.name] = definition
            elif k == "Return":
                if not in_function:
                    self.fail(line, "balek hanya boleh di dalam fungsi")
                raise ReturnSignal(self.expr(n.value, env, depth))
            else:
                self.fail(line, f"pernyataan '{k}' belum didukung")

    def run_module(self, source):
        self.functions.clear()
        self.budget = 0
        tree = parse(source)

        # Register top-level functions before execution, matching native runtime.
        for statement in tree.body:
            if statement.kind != "Function":
                continue
            line = statement.line
            name = statement.name
            if name in ("panjang", "rentang"):
                self.fail(line, f"nama fungsi '{name}' sudah digunakan")
            if name in self.functions:
                self.fail(line, f"fungsi '{name}' sudah dibuat")
            self.functions[name] = (
                statement.params, statement.body, line
            )

        env = {}
        self.block(tree.body, env)
        return env

    def run(self, source):
        self.run_module(source)
        return None


def run(source, source_path=None, project_root=None):
    return Evaluator(source_path=source_path, project_root=project_root).run(source)


def capture(source, source_path=None, project_root=None):
    output = StringIO()
    with redirect_stdout(output):
        run(source, source_path=source_path, project_root=project_root)
    return output.getvalue()
