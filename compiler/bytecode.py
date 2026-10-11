"""Portable stack bytecode compiler for PusingCuk IR v1."""
import json
from compiler.ir import validate


FORMAT = "pusingcuk-bytecode"
VERSION = 1
OPS = {
    "CONST", "LOAD", "DECLARE", "STORE", "PRINT", "INPUT", "POP",
    "MAKE_LIST", "MAKE_DICT", "GET", "SET_INDEX", "UNARY", "BINARY",
    "TO_BOOL", "JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "CALL",
    "ITER_INIT", "ITER_NEXT", "RETURN",
}


class BytecodeError(ValueError):
    pass


class Compiler:
    def __init__(self):
        self.code = []
        self.slot = 0

    def emit(self, op, arg=None, line=1):
        if op not in OPS:
            raise BytecodeError(f"opcode tidak dikenal: {op}")
        self.code.append([op, arg, line])
        return len(self.code) - 1

    def patch(self, index, target):
        self.code[index][1] = target

    def expression(self, n):
        kind, f, line = n["kind"], n["fields"], n["line"]
        if kind == "Literal":
            self.emit("CONST", f["value"], line)
        elif kind == "Variable":
            self.emit("LOAD", f["name"], line)
        elif kind == "List":
            for item in f["items"]: self.expression(item)
            self.emit("MAKE_LIST", len(f["items"]), line)
        elif kind == "Dict":
            for key, value in f["items"]:
                self.expression(key); self.expression(value)
            self.emit("MAKE_DICT", len(f["items"]), line)
        elif kind == "Index":
            self.expression(f["collection"]); self.expression(f["index"])
            self.emit("GET", None, line)
        elif kind == "Unary":
            self.expression(f["value"]); self.emit("UNARY", f["op"], line)
        elif kind == "Binary":
            op = f["op"]
            if op in ("dan", "atau"):
                self.expression(f["left"]); self.emit("TO_BOOL", None, line)
                branch = self.emit("JUMP_IF_FALSE" if op == "dan" else "JUMP_IF_TRUE", None, line)
                self.expression(f["right"]); self.emit("TO_BOOL", None, line)
                end = self.emit("JUMP", None, line)
                self.patch(branch, len(self.code))
                self.emit("CONST", op == "atau", line)
                self.patch(end, len(self.code))
            else:
                self.expression(f["left"]); self.expression(f["right"])
                self.emit("BINARY", op, line)
        elif kind == "Call":
            for arg in f["args"]: self.expression(arg)
            self.emit("CALL", [f["name"], len(f["args"])], line)
        else:
            raise BytecodeError(f"baris {line}: ekspresi belum didukung: {kind}")

    def statements(self, items, in_function=False):
        for stmt in items:
            kind, f, line = stmt["kind"], stmt["fields"], stmt["line"]
            if kind == "Function":
                raise BytecodeError(f"baris {line}: fungsi hanya boleh di tingkat teratas")
            if kind == "Declare":
                self.expression(f["value"]); self.emit("DECLARE", f["name"], line)
            elif kind == "Assign":
                self.expression(f["value"]); self.emit("STORE", f["name"], line)
            elif kind == "Input":
                self.expression(f["prompt"]); self.emit("INPUT", f["name"], line)
            elif kind == "Print":
                self.expression(f["value"]); self.emit("PRINT", None, line)
            elif kind == "IndexAssign":
                self.expression(f["collection"]); self.expression(f["index"]); self.expression(f["value"])
                self.emit("SET_INDEX", None, line)
            elif kind == "If":
                self.expression(f["condition"])
                jump_false = self.emit("JUMP_IF_FALSE", None, line)
                self.statements(f["then_body"], in_function)
                if f["else_body"]:
                    jump_end = self.emit("JUMP", None, line)
                    self.patch(jump_false, len(self.code))
                    self.statements(f["else_body"], in_function)
                    self.patch(jump_end, len(self.code))
                else:
                    self.patch(jump_false, len(self.code))
            elif kind == "While":
                start = len(self.code)
                self.expression(f["condition"])
                end = self.emit("JUMP_IF_FALSE", None, line)
                self.statements(f["body"], in_function)
                self.emit("JUMP", start, line)
                self.patch(end, len(self.code))
            elif kind == "For":
                self.expression(f["iterable"])
                slot = self.slot; self.slot += 1
                self.emit("ITER_INIT", slot, line)
                start = len(self.code)
                end = self.emit("ITER_NEXT", [slot, f["name"], None], line)
                self.statements(f["body"], in_function)
                self.emit("JUMP", start, line)
                self.patch(end, [slot, f["name"], len(self.code)])
            elif kind == "Return":
                if not in_function:
                    raise BytecodeError(f"baris {line}: balek hanya boleh di dalam fungsi")
                if f["value"] is None: self.emit("CONST", None, line)
                else: self.expression(f["value"])
                self.emit("RETURN", None, line)
            else:
                raise BytecodeError(f"baris {line}: pernyataan belum didukung: {kind}")

    def compile_function(self, statement):
        f = statement["fields"]
        compiler = Compiler()
        compiler.statements(f["body"], in_function=True)
        if not compiler.code or compiler.code[-1][0] != "RETURN":
            compiler.emit("CONST", None, statement["line"])
            compiler.emit("RETURN", None, statement["line"])
        return {"params": f["params"], "code": compiler.code}

    def compile(self, document):
        validate(document)
        root = document["program"]
        if root["kind"] != "Program": raise BytecodeError("root IR harus Program")
        functions = {}
        body = root["fields"]["body"]
        for stmt in body:
            if stmt["kind"] != "Function": continue
            name = stmt["fields"]["name"]
            if name in functions or name in ("panjang", "rentang", "mutlak", "minimum", "maksimum", "bulatkan"):
                raise BytecodeError(f"fungsi duplikat atau nama bawaan: {name}")
            functions[name] = self.compile_function(stmt)
        self.statements([s for s in body if s["kind"] != "Function"])
        return {
            "format": FORMAT, "bytecode_version": VERSION,
            "language_version": document["language_version"],
            "source_name": document["source_name"],
            "functions": functions, "code": self.code,
        }


def compile_ir(document):
    return Compiler().compile(document)


def compile_source(source, source_name="<memory>"):
    from compiler.ir import from_source
    return compile_ir(from_source(source, source_name))


def validate_bytecode(document):
    if not isinstance(document, dict) or set(document) != {
        "format", "bytecode_version", "language_version", "source_name", "functions", "code"
    }:
        raise BytecodeError("envelope bytecode tidak valid")
    if document["format"] != FORMAT or document["bytecode_version"] != VERSION:
        raise BytecodeError("format atau versi bytecode tidak didukung")
    if not isinstance(document["code"], list) or len(document["code"]) > 100000:
        raise BytecodeError("instruksi bytecode tidak valid atau melewati batas")
    if not isinstance(document["functions"], dict):
        raise BytecodeError("tabel fungsi bytecode tidak valid")
    for name, fn in document["functions"].items():
        if not isinstance(name, str) or not isinstance(fn, dict) or set(fn) != {"params", "code"}:
            raise BytecodeError("entri fungsi bytecode tidak valid")
        if not isinstance(fn["params"], list) or not isinstance(fn["code"], list):
            raise BytecodeError("parameter atau kode fungsi tidak valid")
        if len(fn["code"]) > 100000: raise BytecodeError("fungsi melewati batas instruksi")
    for code in [document["code"]] + [fn["code"] for fn in document["functions"].values()]:
        for ins in code:
            if not isinstance(ins, list) or len(ins) != 3 or ins[0] not in OPS:
                raise BytecodeError("instruksi bytecode tidak valid")
            if not isinstance(ins[2], int) or isinstance(ins[2], bool) or ins[2] < 1:
                raise BytecodeError("nomor baris bytecode tidak valid")
    return document


def save(document, path):
    validate_bytecode(document)
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(document, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
