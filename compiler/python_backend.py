"""Compile PusingCuk IR to standalone Python source (experimental subset)."""
import argparse
import json
import sys
from pathlib import Path
from compiler.ir import from_source, validate


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
            if f["name"] in functions or f["name"] in ("panjang", "rentang"):
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
        if k == "Dict": return "{" + ", ".join(expr(p[0], env) + ": " + expr(p[1], env) for p in f["items"]) + "}"
        if k == "Index": return f"pc_get({expr(f['collection'], env)}, {expr(f['index'], env)})"
        if k == "Call":
            name, args = f["name"], f["args"]
            values = ", ".join(expr(x, env) for x in args)
            if name == "panjang" and len(args) == 1: return f"len({values})"
            if name == "rentang" and 1 <= len(args) <= 3: return f"list(range({values}))"
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
            else: raise PythonBackendError(f"baris {line}: pernyataan belum didukung: {k}")
        return out

    runtime = '''import math
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
    return a[i]
def pc_set(a, i, v):
    if not isinstance(a, (list, dict)): raise TypeError("nilai tidak dapat diindeks")
    if isinstance(a, list) and (not isinstance(i, int) or isinstance(i, bool) or i < 0 or i >= len(a)): raise IndexError("indeks di luar batas")
    a[i] = v
'''
    out = [runtime, ""]
    for name, s in functions.items():
        f = s["fields"]; env = {p: "pc_v_" + p for p in f["params"]}
        out.append("def pc_fn_" + name + "(" + ", ".join(env[p] for p in f["params"]) + "):")
        out.extend(emit(f["body"], env) or ["    pass"])
        out.append("")
    out.append("# Program utama")
    out.extend(emit([s for s in root["fields"]["body"] if s["kind"] != "Function"], {}) or ["pass"])
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
