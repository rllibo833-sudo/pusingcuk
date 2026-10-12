#!/usr/bin/env python3
"""Offline PVM v1 reader and restricted Python source transpiler; standard library only."""
import ast
import pathlib
import re
import sys

SAFE_RUNTIME = """import ast, pathlib, sys, json
v = {}
__opened = None

def __offline_data(value):
    text = str(value)
    prefix = "data:text/plain,"
    if not text.startswith(prefix):
        raise ValueError("network access is disabled")
    raw = text[len(prefix):]
    output = bytearray()
    index = 0
    while index < len(raw):
        if raw[index] == "%" and index + 2 < len(raw):
            try:
                output.append(int(raw[index + 1:index + 3], 16))
                index += 3
                continue
            except ValueError:
                pass
        output.extend(raw[index].encode("utf-8"))
        index += 1
    return output.decode("utf-8")

def __parse_expression(source):
    root = ast.parse(source, mode="eval").body

    def visit(node):
        if isinstance(node, ast.Constant):
            if type(node.value) in (str, int, float, bool) or node.value is None:
                return node.value
            raise ValueError("literal type is not supported")
        if isinstance(node, ast.Name):
            if node.id in ("True", "False", "None"):
                return {"True": True, "False": False, "None": None}[node.id]
            if node.id not in v:
                raise ValueError("unknown variable: " + node.id)
            return v[node.id]
        if isinstance(node, ast.List):
            return [visit(item) for item in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(visit(item) for item in node.elts)
        if isinstance(node, ast.Dict):
            return {visit(key): visit(value) for key, value in zip(node.keys, node.values)}
        if isinstance(node, ast.Subscript):
            obj = visit(node.value)
            index = visit(node.slice)
            if not isinstance(obj, (list, tuple, str, dict)):
                raise ValueError("indexing this value is not supported")
            if isinstance(obj, (list, tuple, str)):
                if type(index) is not int or index < 0 or index >= len(obj):
                    raise ValueError("index is out of range")
            return obj[index]
        if isinstance(node, ast.UnaryOp):
            value = visit(node.operand)
            if isinstance(node.op, ast.USub) and type(value) in (int, float):
                return -value
            if isinstance(node.op, ast.UAdd) and type(value) in (int, float):
                return +value
            if isinstance(node.op, ast.Not):
                return not value
            raise ValueError("unary operator is not supported")
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                if type(left) is type(right) and type(left) in (int, float, str, list):
                    return left + right
            elif isinstance(node.op, ast.Sub) and type(left) in (int, float) and type(right) in (int, float):
                return left - right
            elif isinstance(node.op, ast.Mult) and type(left) in (int, float) and type(right) in (int, float):
                return left * right
            elif isinstance(node.op, ast.Div) and type(left) in (int, float) and type(right) in (int, float):
                return left / right
            elif isinstance(node.op, ast.FloorDiv) and type(left) in (int, float) and type(right) in (int, float):
                return left // right
            elif isinstance(node.op, ast.Mod) and type(left) in (int, float) and type(right) in (int, float):
                return left % right
            raise ValueError("binary operation is not supported for these values")
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = True
                for item in node.values:
                    result = visit(item)
                    if not result:
                        return result
                return result
            if isinstance(node.op, ast.Or):
                for item in node.values:
                    result = visit(item)
                    if result:
                        return result
                return result
            raise ValueError("boolean operator is not supported")
        if isinstance(node, ast.Compare):
            left = visit(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = visit(comparator)
                if isinstance(op, ast.Eq):
                    ok = type(left) is type(right) and left == right
                elif isinstance(op, ast.NotEq):
                    ok = not (type(left) is type(right) and left == right)
                elif isinstance(op, ast.Lt):
                    ok = type(left) is type(right) and left < right
                elif isinstance(op, ast.LtE):
                    ok = type(left) is type(right) and left <= right
                elif isinstance(op, ast.Gt):
                    ok = type(left) is type(right) and left > right
                elif isinstance(op, ast.GtE):
                    ok = type(left) is type(right) and left >= right
                else:
                    raise ValueError("comparison is not supported")
                if not ok:
                    return False
                left = right
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            functions = {"len": len, "abs": abs, "min": min, "max": max, "round": round}
            if node.func.id not in functions:
                raise ValueError("function is not allowed: " + node.func.id)
            return functions[node.func.id](*(visit(arg) for arg in node.args))
        raise ValueError("expression node is not allowed: " + type(node).__name__)

    return visit(root)

def main():
    global __opened
"""

def read_pvm(filename):
    data = pathlib.Path(filename).read_bytes()
    if len(data) < 6 or data[:4] != b"PVM1" or int.from_bytes(data[4:6], "little") != 1:
        raise ValueError("invalid or unsupported PVM header")
    records = []
    index = 6
    while index < len(data):
        if index + 5 > len(data):
            raise ValueError("truncated PVM record")
        opcode = data[index]
        size = int.from_bytes(data[index + 1:index + 5], "little")
        index += 5
        if size > 1048576 or index + size > len(data):
            raise ValueError("invalid payload length")
        records.append((opcode, data[index:index + size].decode("utf-8")))
        index += size
    return records

def pyexpr(source):
    source = source.strip()
    for word, replacement in (("benar", "True"), ("salah", "False"),
                              ("dan", "and"), ("atau", "or"), ("bukan", "not")):
        source = re.sub(r"\b" + word + r"\b", replacement, source)
    source = re.sub(r"\bpanjang\s*\(", "len(", source)
    return source

def compile_pvm(records):
    out = SAFE_RUNTIME.splitlines()
    indent = 1
    blocks = []

    def emit(line):
        out.append("    " * indent + line)

    def val(source):
        return "__parse_expression(" + repr(pyexpr(source)) + ")"

    for opcode, raw in records:
        arg = raw.strip()
        match = None
        if opcode == 1:
            emit("print(" + val(arg) + ")")
        elif opcode == 2:
            match = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.*)$", arg)
            if match:
                emit("v[" + repr(match.group(1)) + "] = " + val(match.group(2)))
            elif arg:
                emit("v[" + repr(arg) + "] = None")
        elif opcode == 3:
            emit("if " + val(arg) + ":")
            blocks.append("if")
            indent += 1
        elif opcode == 4:
            if blocks and blocks[-1] == "if":
                indent -= 1
                emit("else:")
                indent += 1
            else:
                emit("pass  # alternative branch without a matching condition")
        elif opcode == 5:
            emit("while " + val(arg) + ":")
            blocks.append("mumet")
            indent += 1
        elif opcode == 6:
            match = re.match(r"^([A-Za-z_]\w*)\s+(?:dalam|in)\s+(.+)$", arg)
            if match:
                emit("for __item in " + val(match.group(2)) + ":")
                indent += 1
                emit("v[" + repr(match.group(1)) + "] = __item")
                blocks.append("for")
        elif opcode == 7:
            match = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.*)$", arg)
            if match:
                emit("v[" + repr(match.group(1)) + "] = input(" + val(match.group(2) or "''") + ")")
        elif opcode == 8:
            emit("raise NotImplementedError('function opcode is not supported by PVM v1')")
        elif opcode == 9:
            emit("return " + val(arg or "None"))
        elif opcode == 10:
            emit("__opened = open(" + val(arg) + ", 'a+', encoding='utf-8')")
        elif opcode == 11:
            match = re.match(r"^([A-Za-z_]\w*)\s+(?:dari|from)\s+(.+)$", arg)
            if match:
                emit("v[" + repr(match.group(1)) + "] = pathlib.Path(" + val(match.group(2)) + ").read_text(encoding='utf-8')")
            else:
                emit("print(pathlib.Path(" + val(arg) + ").read_text(encoding='utf-8'))")
        elif opcode == 12:
            emit("pathlib.Path(" + val(arg) + ").unlink(missing_ok=True)")
        elif opcode == 13:
            if arg in ("njir", "mumet", "untuk", "for") and blocks:
                indent = max(1, indent - 1)
                blocks.pop()
            elif arg == "buka":
                emit("__opened.close() if __opened is not None else None")
                emit("__opened = None")
        elif opcode == 14:
            emit("v['__gerombolan'] = " + val(arg))
        elif opcode == 15:
            emit("v['__petik'] = " + val(arg))
        elif opcode == 16:
            match = re.match(r"^([A-Za-z_]\w*)\s*,\s*(.+)$", arg)
            if match:
                emit("v.setdefault(" + repr(match.group(1)) + ", []).append(" + val(match.group(2)) + ")")
            else:
                emit("raise ValueError('cemplungin requires: list_name, value')")
        elif opcode == 17:
            match = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.+)$", arg)
            if match:
                emit("v[" + repr(match.group(1)) + "] = len(" + val(match.group(2)) + ")")
            else:
                emit("print(len(" + val(arg) + "))")
        elif opcode == 18:
            match = re.match(r"^([A-Za-z_]\\w*)\\s*=\\s*(.+)$", arg)
            if match:
                emit("v[" + repr(match.group(1)) + "] = __offline_data(" + val(match.group(2)) + ")")
            else:
                emit("print(__offline_data(" + val(arg) + "))")
        elif opcode == 19:
            emit("print(json.dumps(" + val(arg) + ", ensure_ascii=False, indent=2))")
        else:
            raise ValueError("unknown opcode: " + str(opcode))

    while indent > 1:
        indent -= 1
        emit("pass  # close implicit block")
    out.extend(["if __name__ == '__main__':",
                "    try:",
                "        main()",
                "    except Exception as exc:",
                "        print('PVM runtime:', exc, file=sys.stderr)",
                "        sys.exit(1)", ""])
    return "\n".join(out)

def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: python compiler.py input.pvm [output.py]")
    result = compile_pvm(read_pvm(sys.argv[1]))
    if len(sys.argv) == 3:
        pathlib.Path(sys.argv[2]).write_text(result, encoding="utf-8")
    else:
        sys.stdout.write(result)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("pvm-python:", exc, file=sys.stderr)
        sys.exit(1)
