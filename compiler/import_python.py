"""Importir eksperimental dari subset Python ke sumber Pusingcuk.

Ini bukan transpiler Python umum. Konstruksi di luar subset eksplisit ditolak.
"""
import argparse
import ast
import sys
from pathlib import Path


class ImportErrorPython(ValueError):
    """Python source menggunakan sintaks/semantik yang belum didukung."""


_BINOPS = {
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
    ast.FloorDiv: "//", ast.Mod: "%",
}
_CMPOPS = {
    ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
    ast.Gt: ">", ast.GtE: ">=",
}


def _fail(node, message):
    line = getattr(node, "lineno", 1)
    raise ImportErrorPython(f"baris Python {line}: {message}")


def _quote(value):
    parts = ['"']
    for char in value:
        if char == "\\": parts.append("\\\\")
        elif char == '"': parts.append('\\"')
        elif char == "\n": parts.append("\\n")
        elif char == "\t": parts.append("\\t")
        elif char == "\r": parts.append("\\r")
        elif ord(char) < 32:
            raise ImportErrorPython("karakter kontrol dalam teks belum didukung")
        else: parts.append(char)
    parts.append('"')
    return "".join(parts)


class Importer:
    def __init__(self):
        self.scopes = [set()]
        self.indent = 0
        self.lines = []

    def emit(self, text=""):
        self.lines.append("    " * self.indent + text)

    def expr(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "benar" if node.value else "salah"
            if isinstance(node.value, str):
                return _quote(node.value)
            if isinstance(node.value, int) and not isinstance(node.value, bool):
                return str(node.value)
            if isinstance(node.value, float):
                if node.value != node.value or abs(node.value) == float("inf"):
                    _fail(node, "NaN dan infinity tidak didukung")
                text = repr(node.value)
                if "e" in text.lower():
                    _fail(node, "notasi eksponen belum didukung dalam literal")
                return text
            _fail(node, "literal ini belum didukung")
        if isinstance(node, ast.Name):
            if node.id in ("True", "False"):
                return "benar" if node.id == "True" else "salah"
            if node.id in ("None",):
                _fail(node, "None belum memiliki padanan Pusingcuk")
            return node.id
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return f"({self.expr(node.left)} {_BINOPS[type(node.op)]} {self.expr(node.right)})"
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return f"(bukan {self.expr(node.operand)})"
            if isinstance(node.op, ast.USub):
                return f"(-{self.expr(node.operand)})"
            _fail(node, "operator unary Python ini belum didukung")
        if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
            op = "dan" if isinstance(node.op, ast.And) else "atau"
            return "(" + f" {op} ".join(self.expr(v) for v in node.values) + ")"
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in _CMPOPS:
            return f"({self.expr(node.left)} {_CMPOPS[type(node.ops[0])]} {self.expr(node.comparators[0])})"
        if isinstance(node, ast.List):
            return "[" + ", ".join(self.expr(v) for v in node.elts) + "]"
        if isinstance(node, ast.Dict):
            if any(key is None for key in node.keys):
                _fail(node, "dictionary unpacking belum didukung")
            return "{" + ", ".join(f"{self.expr(k)}: {self.expr(v)}" for k, v in zip(node.keys, node.values)) + "}"
        if isinstance(node, ast.Subscript):
            if isinstance(node.slice, ast.Slice):
                _fail(node, "slicing Python belum didukung")
            return f"{self.expr(node.value)}[{self.expr(node.slice)}]"
        if isinstance(node, ast.Call):
            if node.keywords:
                _fail(node, "argumen bernama Python belum didukung")
            if isinstance(node.func, ast.Name):
                name = node.func.id
                if name == "print":
                    _fail(node, "print() hanya boleh menjadi pernyataan, bukan ekspresi")
                if name == "input":
                    _fail(node, "input() hanya didukung sebagai nilai assignment sederhana")
                aliases = {
                    "len": ("panjang", 1, 1),
                    "range": ("rentang", 1, 3),
                    "abs": ("mutlak", 1, 1),
                    "round": ("bulatkan", 1, 1),
                    "min": ("minimum", 2, 2),
                    "max": ("maksimum", 2, 2),
                }
                if name in aliases:
                    target, min_args, max_args = aliases[name]
                    if not min_args <= len(node.args) <= max_args:
                        _fail(node, f"{name}() pada importer ini membutuhkan {min_args}" +
                              (f" sampai {max_args} argumen" if min_args != max_args else " argumen"))
                    name = target
                return f"{name}(" + ", ".join(self.expr(v) for v in node.args) + ")"
            _fail(node, "pemanggilan melalui atribut/objek belum didukung")
        _fail(node, f"ekspresi Python {type(node).__name__} belum didukung")

    def block(self, statements):
        for stmt in statements:
            self.statement(stmt)

    def statement(self, node):
        if isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "print":
                if node.value.keywords:
                    _fail(node, "print dengan keyword arguments belum didukung")
                if len(node.value.args) != 1:
                    _fail(node, "print() harus memiliki tepat satu argumen")
                self.emit("hedeh " + self.expr(node.value.args[0]))
                return
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return
            _fail(node, "hanya print() dan docstring yang didukung sebagai pernyataan ekspresi")
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1:
                _fail(node, "multiple assignment Python belum didukung")
            target = node.targets[0]
            if isinstance(target, ast.Name):
                name = target.id
                if name in ("True", "False", "None"):
                    _fail(node, "nama literal Python tidak dapat ditimpa")
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "input":
                    if node.value.keywords or len(node.value.args) > 1:
                        _fail(node, "input() menerima paling banyak satu prompt posisional")
                    prompt = self.expr(node.value.args[0]) if node.value.args else _quote("")
                    if name in self.scopes[-1]:
                        _fail(node, f"input assignment ulang ke {name!r} belum didukung; gunakan nama baru")
                    self.emit(f"tanya {name} = {prompt}")
                else:
                    prefix = "lah " if name not in self.scopes[-1] else ""
                    self.emit(f"{prefix}{name} = {self.expr(node.value)}")
                self.scopes[-1].add(name)
                return
            if isinstance(target, ast.Subscript):
                self.emit(f"{self.expr(target.value)}[{self.expr(target.slice)}] = {self.expr(node.value)}")
                return
            _fail(node, "target assignment harus nama variabel atau indeks koleksi")
        if isinstance(node, ast.AnnAssign):
            _fail(node, "type annotations belum didukung")
        if isinstance(node, ast.AugAssign):
            if not isinstance(node.target, ast.Name) or type(node.op) not in _BINOPS:
                _fail(node, "augmented assignment hanya didukung untuk variabel dan operator matematika dasar")
            name = node.target.id
            self.emit(f"{name} = ({name} {_BINOPS[type(node.op)]} {self.expr(node.value)})")
            self.scopes[-1].add(name)
            return
        if isinstance(node, ast.If):
            before = set(self.scopes[-1])
            self.emit("njir " + self.expr(node.test))
            self.indent += 1
            self.scopes[-1] = set(before)
            self.block(node.body)
            then_names = set(self.scopes[-1])
            self.indent -= 1
            else_names = set(before)
            if node.orelse:
                self.emit("kampret")
                self.indent += 1
                self.scopes[-1] = set(before)
                self.block(node.orelse)
                else_names = set(self.scopes[-1])
                self.indent -= 1
            self.scopes[-1] = before | then_names | else_names
            self.emit("selesai njir")
            return
        if isinstance(node, ast.While):
            if node.orelse:
                _fail(node, "while-else Python belum didukung")
            self.emit("mumet " + self.expr(node.test))
            self.indent += 1
            self.block(node.body)
            self.indent -= 1
            self.emit("selesai mumet")
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            if isinstance(node, ast.AsyncFor) or node.orelse:
                _fail(node, "async for dan for-else belum didukung")
            if not isinstance(node.target, ast.Name):
                _fail(node, "target for harus satu nama variabel")
            self.scopes[-1].add(node.target.id)
            self.emit(f"untuk {node.target.id} dalam {self.expr(node.iter)}")
            self.indent += 1
            self.block(node.body)
            self.indent -= 1
            self.emit("selesai untuk")
            return
        if isinstance(node, ast.FunctionDef):
            if node.decorator_list or node.returns or node.type_comment:
                _fail(node, "decorator, return annotation, dan type comment belum didukung")
            if node.args.posonlyargs or node.args.vararg or node.args.kwarg or node.args.kwonlyargs or node.args.defaults or any(node.args.kw_defaults):
                _fail(node, "hanya parameter posisi biasa tanpa nilai default yang didukung")
            if any(not isinstance(arg, ast.arg) or arg.annotation for arg in node.args.args):
                _fail(node, "parameter beranotasi belum didukung")
            params = [arg.arg for arg in node.args.args]
            if len(set(params)) != len(params):
                _fail(node, "nama parameter ganda")
            self.emit(f"fungsi {node.name}(" + ", ".join(params) + ")")
            self.indent += 1
            self.scopes.append(set(params))
            self.block(node.body)
            self.scopes.pop()
            self.indent -= 1
            self.emit("selesai fungsi")
            self.scopes[-1].add(node.name)
            return
        if isinstance(node, ast.Return):
            self.emit("balek" + (" " + self.expr(node.value) if node.value else ""))
            return
        if isinstance(node, ast.Pass):
            return
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            _fail(node, "import Python belum didukung otomatis; modul harus dipetakan ke pustaka Pusingcuk yang benar-benar tersedia")
        if isinstance(node, (ast.ClassDef, ast.Try, ast.Raise, ast.With, ast.AsyncWith, ast.AsyncFunctionDef, ast.Lambda, ast.Match, ast.Global, ast.Nonlocal, ast.Delete, ast.Assert)):
            _fail(node, f"{type(node).__name__} belum didukung")
        _fail(node, f"pernyataan Python {type(node).__name__} belum didukung")

    def translate(self, source, source_name="<python>"):
        try:
            tree = ast.parse(source, filename=source_name)
        except SyntaxError as exc:
            raise ImportErrorPython(f"Python baris {exc.lineno}: {exc.msg}") from exc
        self.emit("jancuk")
        self.block(tree.body)
        self.emit("selesai jancuk")
        return "\n".join(self.lines) + "\n"


def translate(source, source_name="<python>"):
    return Importer().translate(source, source_name)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Terjemahkan subset Python menjadi sumber Pusingcuk")
    parser.add_argument("file", help="berkas Python sumber")
    parser.add_argument("-o", "--output", help="berkas .cuk keluaran; default stdout")
    args = parser.parse_args(argv)
    source_path = Path(args.file)
    if not source_path.is_file():
        print(f"berkas tidak ditemukan: {source_path}", file=sys.stderr)
        return 2
    try:
        result = translate(source_path.read_text(encoding="utf-8"), source_path.name)
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            sys.stdout.write(result)
    except (ImportErrorPython, OSError, UnicodeError) as exc:
        print(f"impor Python gagal: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
