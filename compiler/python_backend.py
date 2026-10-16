"""Compile PusingCuk IR to standalone Python source (experimental subset)."""
import argparse
import json
import sys
from pathlib import Path
from compiler.ir import from_source, validate
from library.builtin_contract import BUILTIN_NAMES, backend_builtins

PYTHON_BACKEND_BUILTINS = backend_builtins("python")


class PythonBackendError(ValueError):
    pass


def generate(document):
    validate(document)
    root = document["program"]
    if root["kind"] != "Program":
        raise PythonBackendError("IR root must be Program")
    functions = {}
    for s in root["fields"]["body"]:
        if s["kind"] == "Function":
            f = s["fields"]
            if f["name"] in functions or f["name"] in BUILTIN_NAMES:
                raise PythonBackendError(f"nama fungsi bentrok: {f['name']}")
            functions[f["name"]] = s

    def expr(n, env):
        k, f, line = n["kind"], n["fields"], n["line"]
        if k == "Literal":
            v = f["value"]
            return "None" if v is None else ("True" if v is True else ("False" if v is False else json.dumps(v, ensure_ascii=False)))
        if k == "Variable":
            if f["name"] not in env: raise PythonBackendError(f"baris {line}: variabel belum dideklarasikan: {f['name']}")
            return env[f["name"]]
        if k == "List": return "[" + ", ".join(expr(x, env) for x in f["items"]) + "]"
        if k == "Dict": return "PcDict([" + ", ".join("(" + expr(p[0], env) + ", " + expr(p[1], env) + ")" for p in f["items"]) + "])"
        if k == "Index": return f"pc_get({expr(f['collection'], env)}, {expr(f['index'], env)})"
        if k == "Call":
            name, args = f["name"], f["args"]
            values = ", ".join(expr(x, env) for x in args)
            builtin = PYTHON_BACKEND_BUILTINS.get(name)
            if builtin is not None:
                if not builtin["min_args"] <= len(args) <= builtin["max_args"]:
                    low, high = builtin["min_args"], builtin["max_args"]
                    expected = str(low) if low == high else f"{low}-{high}"
                    raise PythonBackendError(f"baris {line}: {name} membutuhkan {expected} argumen")
                return f"{builtin['helper']}({values})"
            if name not in functions: raise PythonBackendError(f"baris {line}: fungsi tidak dikenal: {name}")
            if len(args) != len(functions[name]["fields"]["params"]): raise PythonBackendError(f"baris {line}: jumlah argumen salah untuk {name}")
            return f"pc_fn_{name}({values})"
        if k == "Unary":
            value = expr(f["value"], env)
            if f["op"] == "bukan": return f"(not ({value}))"
            if f["op"] == "-": return f"(-({value}))"
        if k == "Binary":
            op, a, b = f["op"], expr(f["left"], env), expr(f["right"], env)
            if op == "==": return f"pc_eq({a}, {b})"
            if op == "!=": return f"(not pc_eq({a}, {b}))"
            if op == "+": return f"pc_add({a}, {b})"
            if op == "/": return f"pc_div({a}, {b})"
            if op == "//": return f"math.floor(pc_div({a}, {b}))"
            if op == "%": return f"pc_mod({a}, {b})"
            if op in ("-", "*", "<", "<=", ">", ">="): return f"(({a}) {op} ({b}))"
            if op == "dan": return f"(bool({a}) and bool({b}))"
            if op == "atau": return f"(bool({a}) or bool({b}))"
        raise PythonBackendError(f"baris {line}: ekspresi belum didukung: {k}")

    def emit(items, env, indent="    ", inside_function=False):
        out = []
        for s in items:
            k, f, line = s["kind"], s["fields"], s["line"]
            if k == "Function": raise PythonBackendError("fungsi hanya boleh di tingkat teratas")
            if k == "Declare":
                name = f["name"]
                if name in env: raise PythonBackendError(f"baris {line}: variabel sudah dideklarasikan: {name}")
                env[name] = "pc_v_" + name
                out.append(indent + env[name] + " = " + expr(f["value"], env))
            elif k == "Assign":
                if f["name"] not in env: raise PythonBackendError(f"baris {line}: variabel belum dideklarasikan: {f['name']}")
                out.append(indent + env[f["name"]] + " = " + expr(f["value"], env))
            elif k == "Print": out.append(indent + "pc_out(" + expr(f["value"], env) + ")")
            elif k == "Input":
                name = f["name"]
                if name in env: raise PythonBackendError(f"baris {line}: variabel input sudah dideklarasikan: {name}")
                env[name] = "pc_v_" + name
                out.append(indent + env[name] + " = input(" + expr(f["prompt"], env) + ")")
            elif k == "IndexAssign":
                out.append(indent + "pc_set(" + expr(f["collection"], env) + ", " + expr(f["index"], env) + ", " + expr(f["value"], env) + ")")
            elif k == "Return":
                if not inside_function: raise PythonBackendError(f"baris {line}: balek di luar fungsi")
                out.append(indent + "return " + (expr(f["value"], env) if f["value"] is not None else "None"))
            elif k == "If":
                condition = expr(f["condition"], env)
                then_env, else_env = dict(env), dict(env)
                yes = emit(f["then_body"], then_env, indent + "    ", inside_function)
                no = emit(f["else_body"], else_env, indent + "    ", inside_function)
                out.append(indent + "if " + condition + ":")
                out.extend(yes or [indent + "    pass"])
                if f["else_body"]:
                    out.append(indent + "else:")
                    out.extend(no or [indent + "    pass"])
            elif k == "While":
                out.append(indent + "pc_count = 0")
                out.append(indent + "while " + expr(f["condition"], env) + ":")
                out.append(indent + "    pc_count += 1")
                out.append(indent + "    if pc_count > 10000: raise RuntimeError('batas loop')")
                out.extend(emit(f["body"], env, indent + "    ", inside_function) or [indent + "    pass"])
            elif k == "For":
                name = f["name"]
                if name in env: raise PythonBackendError(f"baris {line}: nama loop sudah digunakan: {name}")
                loop_env = dict(env); loop_env[name] = "pc_v_" + name
                out.append(indent + "for " + loop_env[name] + " in " + expr(f["iterable"], env) + ":")
                out.extend(emit(f["body"], loop_env, indent + "    ", inside_function) or [indent + "    pass"])
            elif k == "Try":
                body, handler_name = f["body"], f["handler_name"]
                handler, final = f["handler"], f["final"]
                if handler_name is not None and (not isinstance(handler_name, str) or not handler_name.isidentifier()):
                    raise PythonBackendError(f"baris {line}: nama variabel ketangkep tidak valid")
                if handler_name is None and not final:
                    out.extend(emit(body, env, indent, inside_function) or [])
                    continue
                out.append(indent + "try:")
                out.extend(emit(body, dict(env), indent + "    ", inside_function) or [indent + "    pass"])
                if handler_name is not None:
                    error_name = "pc_error_" + str(line)
                    catch_name = "pc_catch_" + handler_name + "_" + str(line)
                    handler_env = dict(env)
                    handler_env[handler_name] = catch_name
                    out.append(indent + "except Exception as " + error_name + ":")
                    out.append(indent + "    " + catch_name + " = str(" + error_name + ")")
                    out.extend(emit(handler, handler_env, indent + "    ", inside_function) or [indent + "    pass"])
                if final:
                    out.append(indent + "finally:")
                    out.extend(emit(final, dict(env), indent + "    ", inside_function) or [indent + "    pass"])
            else: raise PythonBackendError(f"baris {line}: pernyataan belum didukung: {k}")
        return out

    runtime = '''import math
class PcDict:
    def __init__(self, pairs=()):
        self.entries = []
        for key, value in pairs: self[key] = value
    @staticmethod
    def same(a, b):
        if isinstance(a, bool) or isinstance(b, bool): return type(a) is type(b) and a == b
        if isinstance(a, (int, float)) and isinstance(b, (int, float)): return a == b
        return type(a) is type(b) and a == b
    def index(self, key):
        if not isinstance(key, (str, int, float, bool)): raise TypeError("kunci kamus harus teks, angka, atau boolean")
        for i, (old, _) in enumerate(self.entries):
            if self.same(old, key): return i
        return -1
    def __getitem__(self, key):
        i = self.index(key)
        if i < 0: raise KeyError("kunci kamus tidak ditemukan")
        return self.entries[i][1]
    def __setitem__(self, key, value):
        i = self.index(key)
        if i < 0: self.entries.append((key, value))
        else: self.entries[i] = (self.entries[i][0], value)
    def __iter__(self): return (key for key, _ in self.entries)
    def __len__(self): return len(self.entries)
def pc_numeric(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise TypeError(name + " membutuhkan angka finite")
    return value
def pc_abs(value): return abs(pc_numeric("mutlak", value))
def pc_min(a, b): return min(pc_numeric("minimum", a), pc_numeric("minimum", b))
def pc_max(a, b): return max(pc_numeric("maksimum", a), pc_numeric("maksimum", b))
def pc_round(value):
    value = pc_numeric("bulatkan", value)
    lower = math.floor(value)
    fraction = value - lower
    if fraction < 0.5: return lower
    if fraction > 0.5: return lower + 1
    return lower if lower % 2 == 0 else lower + 1
def pc_math_result(name, value):
    if not math.isfinite(value): raise ValueError(name + " menghasilkan angka di luar domain atau non-finite")
    return value
def pc_sqrt(value):
    value = pc_numeric("akar", value)
    if value < 0: raise ValueError("akar() domain tidak valid: angka harus non-negatif")
    return pc_math_result("akar", math.sqrt(value))
def pc_floor(value): return math.floor(pc_numeric("bawah", value))
def pc_ceil(value): return math.ceil(pc_numeric("atas", value))
def pc_pow(a, b): return pc_math_result("pangkat", math.pow(pc_numeric("pangkat", a), pc_numeric("pangkat", b)))
def pc_sin(value): return pc_math_result("sinus", math.sin(pc_numeric("sinus", value)))
def pc_cos(value): return pc_math_result("kosinus", math.cos(pc_numeric("kosinus", value)))
def pc_stat_values(name, value):
    if not isinstance(value, list) or not value:
        raise TypeError(name + "() membutuhkan daftar angka yang tidak kosong")
    values = [pc_numeric(name, item) for item in value]
    if any(
        (isinstance(item, int) and abs(item) > 9007199254740991)
        or (isinstance(item, float) and item.is_integer() and abs(item) > 9007199254740991)
        for item in values
    ):
        raise ValueError(name + "() menolak integer di luar rentang aman lintas target")
    return values
def pc_stat_result(name, value):
    if not math.isfinite(value): raise ValueError(name + "() menghasilkan angka non-finite")
    if value.is_integer() and abs(value) <= 9007199254740991: return int(value)
    return value
def pc_mean(value):
    values = pc_stat_values("rata_rata", value)
    try:
        count = len(values)
        return pc_stat_result("rata_rata", sum(item / count for item in values))
    except OverflowError as exc: raise ValueError("rata_rata() menghasilkan angka non-finite") from exc
def pc_median(value):
    values = sorted(pc_stat_values("median", value))
    middle = len(values) // 2
    if len(values) % 2:
        result = values[middle]
        if isinstance(result, int) and abs(result) <= 9007199254740991: return result
        return pc_stat_result("median", float(result))
    return pc_stat_result("median", values[middle - 1] / 2 + values[middle] / 2)
def pc_range(*args):
    if not 1 <= len(args) <= 3 or any(not isinstance(x, int) or isinstance(x, bool) for x in args): raise TypeError("rentang membutuhkan 1-3 integer")
    if len(args) == 3 and args[2] == 0: raise ValueError("langkah rentang tidak boleh nol")
    result = range(*args)
    if len(result) > 10000: raise ValueError("rentang melewati batas 10000 item")
    return result
def pc_out(v):
    if v is True: v = "okelah"
    elif v is False: v = "tidak"
    elif v is None: v = "kosong"
    print(v)
def pc_eq(a, b):
    if isinstance(a, bool) != isinstance(b, bool) and isinstance(a, (bool, int, float)) and isinstance(b, (bool, int, float)): return False
    if isinstance(a, list) and isinstance(b, list): return len(a) == len(b) and all(pc_eq(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b
def pc_add(a, b):
    v = a + b
    if isinstance(v, float) and not math.isfinite(v): raise OverflowError("angka non-finite")
    return v
def pc_div(a, b):
    if b == 0: raise ZeroDivisionError("pembagian dengan nol")
    v = a / b
    if not math.isfinite(v): raise OverflowError("angka non-finite")
    return v
def pc_mod(a, b):
    if b == 0: raise ZeroDivisionError("modulo dengan nol")
    return a % b
def pc_get(a, i):
    if isinstance(a, (str, list)):
        if not isinstance(i, int) or isinstance(i, bool) or i < 0 or i >= len(a): raise IndexError("indeks di luar batas")
        return a[i]
    if isinstance(a, PcDict): return a[i]
    if isinstance(a, dict): return a[i]
    raise TypeError("nilai tidak dapat diindeks")
def pc_set(a, i, v):
    if not isinstance(a, (list, dict, PcDict)): raise TypeError("nilai tidak dapat diindeks")
    if isinstance(a, list) and (not isinstance(i, int) or isinstance(i, bool) or i < 0 or i >= len(a)): raise IndexError("indeks di luar batas")
    a[i] = v
'''
    out = [runtime, ""]
    for name, s in functions.items():
        f = s["fields"]; env = {p: "pc_v_" + p for p in f["params"]}
        out.append("def pc_fn_" + name + "(" + ", ".join(env[p] for p in f["params"]) + "):")
        out.extend(emit(f["body"], env, inside_function=True) or ["    pass"])
        out.append("")
    out.append("# Program utama")
    out.extend(emit([s for s in root["fields"]["body"] if s["kind"] != "Function"], {}, indent="") or ["pass"])
    return "\n".join(out) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description="Kompilasi PusingCuk ke Python")
    p.add_argument("file")
    p.add_argument("-o", "--output")
    a = p.parse_args(argv)
    path = Path(a.file)
    if not path.is_file():
        print(f"berkas tidak ditemukan: {path}", file=sys.stderr); return 2
    try:
        result = generate(from_source(path.read_text(encoding="utf-8"), path.name))
        if a.output: Path(a.output).write_text(result, encoding="utf-8")
        else: sys.stdout.write(result)
    except (SyntaxError, ValueError, TypeError, OSError) as e:
        print(f"kompilasi Python gagal: {e}", file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
