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
            # Unresolved names are left for runtime lookup; this preserves
            # short-circuit behavior and reference-runtime diagnostics.
            return env.get(f["name"], "pc_v_" + f["name"])
        if k == "List": return "[" + ", ".join(expr(x, env) for x in f["items"]) + "]"
        if k == "Dict": return "PcDict([" + ", ".join("(" + expr(p[0], env) + ", " + expr(p[1], env) + ")" for p in f["items"]) + "])"
        if k == "Index": return f"pc_get({expr(f['collection'], env)}, {expr(f['index'], env)})"
        if k == "Call":
            name, args = f["name"], f["args"]
            values = ", ".join(expr(x, env) for x in args)
            if name in {"jadi_json", "parse_json"}: return f"pc_json_parse({values})"
            if name == "jadi_teks": return f"pc_json_text({values})"
            builtin = PYTHON_BACKEND_BUILTINS.get(name)
            if builtin is not None:
                if builtin["min_args"] <= len(args) <= builtin["max_args"]:
                    return f"{builtin['helper']}({values})"
                return (f"pc_invoke_builtin({json.dumps(name)}, [{values}], "
                        f"{builtin['min_args']}, {builtin['max_args']}, "
                        f"lambda *pc_args: {builtin['helper']}(*pc_args))")
            if name not in functions: raise PythonBackendError(f"baris {line}: fungsi tidak dikenal: {name}")
            expected = len(functions[name]["fields"]["params"])
            if len(args) == expected: return f"pc_fn_{name}({values})"
            return f"pc_invoke_function({json.dumps(name)}, [{values}], {expected}, pc_fn_{name})"
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
            out.append(indent + "pc_current_line = " + str(line))
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
import sys
import json
import html
import csv
import io
pc_current_line = 0
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
    def __repr__(self):
        return "{" + ", ".join(repr(key) + ": " + repr(value) for key, value in self.entries) + "}"
def pc_numeric(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise TypeError(name + " membutuhkan angka finite")
    return value
def pc_safe_integer_result(name, value):
    if abs(value) > 9007199254740991:
        raise ValueError(name + ": hasil integer di luar rentang aman lintas target")
    return value
def pc_abs(value): return abs(pc_numeric("mutlak", value))
def pc_min(a, b): return min(pc_numeric("minimum", a), pc_numeric("minimum", b))
def pc_max(a, b): return max(pc_numeric("maksimum", a), pc_numeric("maksimum", b))
def pc_round(value):
    value = pc_numeric("bulatkan", value)
    lower = math.floor(value)
    fraction = value - lower
    if fraction < 0.5: result = lower
    elif fraction > 0.5: result = lower + 1
    else: result = lower if lower % 2 == 0 else lower + 1
    return pc_safe_integer_result("bulatkan", result)
def pc_math_result(name, value):
    if not math.isfinite(value): raise ValueError(name + " menghasilkan angka di luar domain atau non-finite")
    return value
def pc_sqrt(value):
    value = pc_numeric("akar", value)
    if value < 0: raise ValueError("akar() domain tidak valid: angka harus non-negatif")
    return pc_math_result("akar", math.sqrt(value))
def pc_floor(value): return pc_safe_integer_result("bawah", math.floor(pc_numeric("bawah", value)))
def pc_ceil(value): return pc_safe_integer_result("atas", math.ceil(pc_numeric("atas", value)))
def pc_pow(a, b): return pc_math_result("pangkat", math.pow(pc_numeric("pangkat", a), pc_numeric("pangkat", b)))
def pc_sin(value): return pc_math_result("sinus", math.sin(pc_numeric("sinus", value)))
def pc_cos(value): return pc_math_result("kosinus", math.cos(pc_numeric("kosinus", value)))
def pc_text(value):
    if value is True: return "okelah"
    if value is False: return "tidak"
    return str(value)
def pc_integer(value):
    if isinstance(value, bool) or value is None:
        raise TypeError("bilangan() tidak menerima boolean atau None")
    if isinstance(value, int): result = value
    elif isinstance(value, float) and math.isfinite(value): result = int(value)
    elif isinstance(value, str):
        try: result = int(value.strip())
        except ValueError as exc: raise ValueError("bilangan() membutuhkan teks integer") from exc
    else: raise TypeError("bilangan() membutuhkan angka atau teks integer")
    if abs(result) > 9007199254740991:
        raise ValueError("bilangan() di luar rentang aman lintas target")
    return result
def pc_float(value):
    if isinstance(value, bool) or value is None:
        raise TypeError("desimal() tidak menerima boolean atau None")
    try: result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("desimal() membutuhkan angka atau teks angka") from exc
    if not math.isfinite(result): raise ValueError("desimal() membutuhkan angka finite")
    return result
def pc_boolean(value):
    return bool(value)
def pc_log(value):
    value = pc_numeric("logaritma", value)
    if value <= 0: raise ValueError("logaritma() domain tidak valid: angka harus lebih besar dari nol")
    return pc_stat_result("logaritma", math.log(value))
def pc_log10(value):
    value = pc_numeric("log10", value)
    if value <= 0: raise ValueError("log10() domain tidak valid: angka harus lebih besar dari nol")
    return pc_stat_result("log10", math.log10(value))
def pc_sum(value):
    if not isinstance(value, list): raise TypeError("jumlah() membutuhkan daftar angka finite")
    total = 0.0
    for item in value:
        item = pc_numeric("jumlah", item)
        if ((isinstance(item, int) and abs(item) > 9007199254740991)
            or (isinstance(item, float) and item.is_integer() and abs(item) > 9007199254740991)):
            raise ValueError("jumlah() menolak angka di luar rentang aman lintas target")
        total += float(item)
        if not math.isfinite(total): raise ValueError("jumlah() menghasilkan angka non-finite")
        if total.is_integer() and abs(total) > 9007199254740991:
            raise ValueError("jumlah() menghasilkan integer di luar rentang aman lintas target")
    return int(total) if total.is_integer() else total
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
def pc_invoke_builtin(name, args, minimum, maximum, function):
    if not minimum <= len(args) <= maximum:
        expected = str(minimum) if minimum == maximum else f"{minimum}-{maximum}"
        raise TypeError(f"{name}() membutuhkan {expected} argumen")
    return function(*args)
def pc_invoke_function(name, args, expected, function):
    if len(args) != expected: raise TypeError(f"fungsi '{name}' membutuhkan {expected} argumen")
    return function(*args)
def pc_format_text(value, name):
    if isinstance(value, str):
        if "\x00" in value: raise ValueError(name + "() tidak menerima NUL")
        if len(value.encode("utf-8")) > 1023: raise ValueError(name + "() teks melebihi batas 1023 byte")
        return value
    if value is None: return "None"
    if value is True: return "okelah"
    if value is False: return "tidak"
    if isinstance(value, int):
        if abs(value) > 9007199254740991: raise ValueError(name + "() integer di luar rentang aman")
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError(name + "() membutuhkan angka finite")
        if value.is_integer() and abs(value) > 9007199254740991:
            raise ValueError(name + "() integer di luar rentang aman")
        return str(int(value)) if value == 0 or value.is_integer() else str(value)
    raise TypeError(name + "() hanya menerima nilai skalar")
def pc_json_value(value, path="$", depth=0, seen=None):
    if depth > 64: raise ValueError("JSON melebihi kedalaman maksimum: " + path)
    if seen is None: seen = set()
    if value is None or isinstance(value, bool): return value
    if isinstance(value, str):
        if "\x00" in value: raise ValueError("JSON teks mengandung NUL: " + path)
        if len(value.encode("utf-8")) > 1023: raise ValueError("JSON teks melebihi 1023 byte: " + path)
        return value
    if isinstance(value, int):
        if abs(value) > 9007199254740991: raise ValueError("JSON integer di luar rentang aman: " + path)
        return value
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError("JSON angka non-finite: " + path)
        if value.is_integer() and abs(value) > 9007199254740991:
            raise ValueError("JSON integer di luar rentang aman: " + path)
        if value == 0 or value.is_integer(): return int(value)
        return value
    if isinstance(value, (PcDict, dict, list)):
        identity = id(value)
        if identity in seen: raise ValueError("JSON tidak menerima struktur melingkar: " + path)
        seen.add(identity)
        try:
            if isinstance(value, PcDict):
                entries = value.entries
                result = {}
                for key, item in entries:
                    if not isinstance(key, str): raise TypeError("kunci objek JSON harus teks: " + path)
                    pc_json_value(key, path + ".<kunci>", depth, seen)
                    result[key] = pc_json_value(item, path + "." + key, depth + 1, seen)
                return result
            if isinstance(value, dict):
                result = {}
                for key, item in value.items():
                    if not isinstance(key, str): raise TypeError("kunci objek JSON harus teks: " + path)
                    pc_json_value(key, path + ".<kunci>", depth, seen)
                    result[key] = pc_json_value(item, path + "." + key, depth + 1, seen)
                return result
            return [pc_json_value(item, path + "[" + str(index) + "]", depth + 1, seen)
                    for index, item in enumerate(value)]
        finally:
            seen.remove(identity)
    raise TypeError("nilai tidak dapat diserialisasi sebagai JSON: " + path)
def pc_json_text(value):
    encoded = json.dumps(pc_json_value(value), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if len(encoded.encode("utf-8")) > 1023: raise ValueError("json_teks() melebihi batas output 1023 byte")
    return encoded
def pc_json_read(value):
    if not isinstance(value, str): raise TypeError("json_baca() membutuhkan teks JSON")
    if "\x00" in value: raise ValueError("json_baca() tidak menerima NUL")
    if len(value.encode("utf-8")) > 1023: raise ValueError("json_baca() input melebihi batas 1023 byte")
    try:
        decoded = json.loads(value, parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
    except (ValueError, TypeError) as exc:
        raise ValueError("teks JSON tidak valid: " + str(exc)) from exc
    return pc_json_value(decoded)
def pc_json_parse(value):
    if not isinstance(value, str): return False
    try: return json.loads(value)
    except (ValueError, TypeError): return False
def pc_html_escape(value):
    text = pc_format_text(value, "html_aman")
    escaped = html.escape(text, quote=True)
    if len(escaped.encode("utf-8")) > 1023: raise ValueError("html_aman() melebihi batas output 1023 byte")
    return escaped
def pc_csv_row(value):
    if not isinstance(value, list): raise TypeError("csv_baris() membutuhkan daftar")
    fields = [pc_format_text(item, "csv_baris") for item in value]
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="").writerow(fields)
    result = buffer.getvalue()
    if len(result.encode("utf-8")) > 1023: raise ValueError("csv_baris() melebihi batas output 1023 byte")
    return result
def pc_out(v):
    if v is True: v = "okelah"
    elif v is False: v = "tidak"
    elif v is None: v = "None"
    elif isinstance(v, float) and v.is_integer() and abs(v) <= 9007199254740991: v = int(v)
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
    if isinstance(a, (str, list, range)):
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
        out.append("    global pc_current_line")
        out.extend(emit(f["body"], env, inside_function=True) or ["    pass"])
        out.append("")
    out.append("# Program utama")
    out.append("try:")
    out.extend(emit([s for s in root["fields"]["body"] if s["kind"] != "Function"], {}, indent="    ") or ["    pass"])
    out.append("except Exception as pc_error:")
    out.append("    print(f\"Kesalahan runtime: Baris {pc_current_line}: {pc_error}\", file=sys.stderr)")
    out.append("    sys.exit(1)")
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
