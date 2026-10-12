"""Evaluator terpisah untuk AST dari parser.py."""
from contextlib import redirect_stdout
from collections.abc import MutableMapping
from io import StringIO
from pathlib import Path
from ast_nodes import Node
from parser import parse


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


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Evaluator:
    def __init__(self):
        self.functions = {}
        self.budget = 0

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
                if n.name == "tanya":
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, "tanya membutuhkan satu prompt teks")
                    return input(args[0])
                if n.name == "tulis":
                    if len(args) != 2 or not all(isinstance(x, str) for x in args):
                        self.fail(line, "tulis membutuhkan path dan teks berupa string")
                    try:
                        Path(args[0]).write_text(args[1], encoding="utf-8")
                        return True
                    except OSError:
                        return False
                if n.name == "baca":
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, "baca membutuhkan satu path berupa string")
                    try:
                        return Path(args[0]).read_text(encoding="utf-8")
                    except FileNotFoundError:
                        return False
                    except OSError:
                        return False
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

    def run(self, source):
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

        self.block(tree.body, {})
        return None


def run(source):
    return Evaluator().run(source)


def capture(source):
    output = StringIO()
    with redirect_stdout(output):
        run(source)
    return output.getvalue()
