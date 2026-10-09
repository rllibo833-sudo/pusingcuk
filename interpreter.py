
import ast
import io
import math
import operator
import re
import sys
import tokenize
from pathlib import Path

BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
CMPOPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}
UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Not: operator.not_,
}


def fail(line, message):
    raise SyntaxError(f"Baris {line}: {message}")


def expression(source, variables, line):
    if len(source) > 10000:
        fail(line, "ekspresi terlalu panjang (maksimal 10000 karakter)")
    replacements = {
        "benar": "True",
        "salah": "False",
        "dan": "and",
        "atau": "or",
        "bukan": "not",
    }

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        fail(line, "ekspresi tidak valid: token tidak lengkap")
    converted = []
    for token in tokens:
        value = token.string
        if token.type == tokenize.NAME:
            value = replacements.get(value, value)
        converted.append(
            (token.type, value)
        )
    source = tokenize.untokenize(converted)

    try:
        tree = ast.parse(source, mode="eval")
    except RecursionError:
        fail(line, "ekspresi terlalu dalam")
    except SyntaxError:
        fail(line, "ekspresi tidak valid")

    def visit(node):
        if isinstance(node, ast.Name):
            if node.id not in variables:
                fail(line, f"variabel '{node.id}' belum ada")
            return variables[node.id]
        if isinstance(node, ast.Constant):
            if type(node.value) is int and node.value.bit_length() > 4096:
                fail(line, "angka terlalu besar (maksimal 4096 bit)")
            if type(node.value) is float and not math.isfinite(node.value):
                fail(line, "angka desimal tidak valid atau terlalu besar")
            if isinstance(node.value, (str, int, float, bool)):
                return node.value
            fail(line, "tipe nilai tidak didukung")

        if isinstance(node, ast.List):
            if any(isinstance(item, ast.List) for item in node.elts):
                fail(line, "daftar bersarang belum didukung")
            return [visit(item) for item in node.elts]

        if isinstance(node, ast.Subscript):
            daftar = visit(node.value)

            if not isinstance(daftar, list):
                fail(line, "indeks hanya dapat digunakan pada daftar")

            indeks_node = node.slice
            if (
                isinstance(indeks_node, ast.UnaryOp)
                and isinstance(indeks_node.op, ast.USub)
                and isinstance(indeks_node.operand, ast.Constant)
                and type(indeks_node.operand.value) is int
            ):
                indeks = -indeks_node.operand.value
            elif isinstance(indeks_node, ast.Constant) and type(indeks_node.value) is int:
                indeks = indeks_node.value
            else:
                fail(line, "indeks harus berupa bilangan bulat")

            if indeks < 0 or indeks >= len(daftar):
                fail(line, "indeks daftar di luar batas")

            return daftar[indeks]

        if isinstance(node, ast.BinOp) and type(node.op) in BINOPS:
            kiri = visit(node.left)
            kanan = visit(node.right)
            if isinstance(node.op, ast.Mult):
                if isinstance(kiri, (str, list)) and type(kanan) is int and len(kiri) * max(kanan, 0) > 100000:
                    fail(line, "hasil perkalian terlalu besar (maksimal 100000 elemen)")
                if isinstance(kanan, (str, list)) and type(kiri) is int and len(kanan) * max(kiri, 0) > 100000:
                    fail(line, "hasil perkalian terlalu besar (maksimal 100000 elemen)")
            if isinstance(node.op, ast.Add) and isinstance(kiri, (str, list)) and type(kanan) is type(kiri) and len(kiri) + len(kanan) > 100000:
                fail(line, "hasil penggabungan terlalu besar (maksimal 100000 elemen)")
            hasil = BINOPS[type(node.op)](kiri, kanan)
            if type(hasil) is int and hasil.bit_length() > 4096:
                fail(line, "hasil angka terlalu besar (maksimal 4096 bit)")
            if type(hasil) is float and not math.isfinite(hasil):
                fail(line, "hasil angka desimal terlalu besar atau tidak valid")
            return hasil

        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARYOPS:
            return UNARYOPS[type(node.op)](visit(node.operand))

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                fail(line, "pemanggilan fungsi tidak didukung")
            if node.func.id == "panjang":
                if len(node.args) != 1 or node.keywords:
                    fail(line, "panjang() membutuhkan satu daftar")
                daftar = visit(node.args[0])
                if not isinstance(daftar, list):
                    fail(line, "panjang() hanya menerima daftar")
                return len(daftar)
            fail(line, "fungsi tidak dikenal")

        if isinstance(node, ast.Compare):
            left = visit(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                if type(op) not in CMPOPS:
                    fail(line, "operator perbandingan tidak didukung")
                right = visit(comparator)
                if not CMPOPS[type(op)](left, right):
                    return False
                left = right
            return True

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(visit(v) for v in node.values)
            if isinstance(node.op, ast.Or):
                return any(visit(v) for v in node.values)

        fail(line, "ekspresi tidak didukung")

    try:
        return visit(tree.body)
    except SyntaxError:
        raise
    except RecursionError:
        fail(line, "ekspresi terlalu dalam")
    except ZeroDivisionError:
        fail(line, "pembagian dengan nol")
    except TypeError:
        fail(line, "tipe data tidak cocok untuk operasi ini")
    except Exception as exc:
        fail(line, f"ekspresi gagal: {exc}")


def parse(lines, pos=0, stops=()):
    nodes = []

    while pos < len(lines):
        line_no, raw = lines[pos]
        text = raw.strip()
        pos += 1

        if not text or text.startswith("#"):
            continue

        if text in stops:
            return nodes, pos - 1, text

        if text.startswith("njir "):
            condition = text[5:].strip()
            yes, pos, ending = parse(
                lines, pos, ("kampret", "selesai njir")
            )
            no = []

            if ending == "kampret":
                no, pos, ending = parse(
                    lines, pos + 1, ("selesai njir",)
                )

            if ending != "selesai njir":
                fail(line_no, "blok njir belum ditutup")

            nodes.append(("if", line_no, condition, yes, no))
            pos += 1
            continue

        if text.startswith("mumet "):
            condition = text[6:].strip()
            body, pos, ending = parse(
                lines, pos, ("selesai mumet",)
            )
            if ending != "selesai mumet":
                fail(line_no, "blok mumet belum ditutup")

            nodes.append(("while", line_no, condition, body))
            pos += 1
            continue

        if text == "kampret" or text.startswith("selesai "):
            fail(line_no, f"penutup blok tidak terduga: {text}")

        if text.startswith("lah "):
            match = re.fullmatch(
                r"lah\s+([A-Za-z_]\w*)\s*=\s*(.+)", text
            )
            if not match:
                fail(line_no, "gunakan lah nama = ekspresi")
            nodes.append(
                ("let", line_no, match.group(1), match.group(2))
            )
            continue

        if text.startswith("hedeh "):
            nodes.append(("print", line_no, text[6:].strip()))
            continue

        match = re.fullmatch(
            r"([A-Za-z_]\w*)\s*\[\s*(-?\d+)\s*\]\s*=(?!=)\s*(.+)",
            text,
        )
        if match:
            nodes.append(
                (
                    "list_assign",
                    line_no,
                    match.group(1),
                    int(match.group(2)),
                    match.group(3),
                )
            )
            continue
        match = re.fullmatch(
            r"([A-Za-z_]\w*)\s*=(?!=)\s*(.+)", text
        )
        if match:
            nodes.append(
                ("assign", line_no, match.group(1), match.group(2))
            )
            continue

        fail(line_no, f"perintah tidak dikenal: {text}")

    return nodes, pos, None


def execute(nodes, variables, budget=None):
    if budget is None:
        budget = [0]
    for node in nodes:
        kind, line = node[0], node[1]
        budget[0] += 1
        if budget[0] > 100000:
            fail(line, "batas total 100000 langkah tercapai")

        if kind == "let":
            _, line, name, source = node
            if name in variables:
                fail(line, f"variabel '{name}' sudah dibuat")
            variables[name] = expression(source, variables, line)

        elif kind == "assign":
            _, line, name, source = node
            if name not in variables:
                fail(line, f"variabel '{name}' belum dibuat")
            variables[name] = expression(source, variables, line)

        elif kind == "list_assign":
            _, line, name, index, source = node
            if name not in variables:
                fail(line, f"variabel '{name}' belum dibuat")
            daftar = variables[name]
            if not isinstance(daftar, list):
                fail(line, "indeks hanya dapat digunakan pada daftar")
            if index < 0 or index >= len(daftar):
                fail(line, "indeks daftar di luar batas")
            daftar[index] = expression(source, variables, line)

        elif kind == "print":
            print(expression(node[2], variables, line))

        elif kind == "if":
            _, line, condition, yes, no = node
            branch = yes if expression(
                condition, variables, line
            ) else no
            execute(branch, variables, budget)

        elif kind == "while":
            _, line, condition, body = node
            count = 0
            while expression(condition, variables, line):
                budget[0] += 1
                if budget[0] > 100000:
                    fail(line, "batas total 100000 langkah tercapai")
                if count >= 10000:
                    fail(line, "batas 10000 iterasi tercapai")
                execute(body, variables, budget)
                count += 1


def run(source):
    lines = [
        (i, text)
        for i, text in enumerate(source.splitlines(), 1)
    ]
    lines = [(i, t) for i, t in lines if t.strip()]

    if len(lines) < 2 or lines[0][1].strip() != "jancuk":
        raise SyntaxError("Program harus dimulai dengan 'jancuk'")

    if lines[-1][1].strip() != "selesai jancuk":
        raise SyntaxError("Program harus diakhiri 'selesai jancuk'")

    nodes, pos, ending = parse(lines[1:-1])

    if ending is not None or pos != len(lines) - 2:
        raise SyntaxError("Struktur program tidak valid")

    execute(nodes, {})


def main():
    if len(sys.argv) != 2:
        print("Pemakaian: pusingcuk program.pusingcuk")
        sys.exit(1)

    try:
        run(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, tokenize.TokenError) as exc:
        print(f"pusingcuk error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
