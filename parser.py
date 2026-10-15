"""Parser Pusingcuk: token lexer -> AST."""
import re

from lexer import lex, LexerError
from ast_nodes import node


class ParserError(SyntaxError):
    """Raised when source text cannot be parsed as valid Pusingcuk syntax."""



def _diagnostic_suggestion(message):
    """Return one useful next step without changing the underlying error class."""
    lower = message.lower()
    if "balek butuh ekspresi" in lower:
        return "Tambahkan nilai setelah 'balek', misalnya: balek hasil."
    if "string belum ditutup" in lower or "string tidak boleh melewati baris" in lower:
        return "Tutup teks dengan tanda kutip yang sama sebelum akhir baris."
    if "escape tidak dikenal" in lower or "escape string tidak lengkap" in lower or "escape baris baru" in lower:
        return "Periksa escape string; yang didukung antara lain \\n, \\t, dan \\\\."
    if "eksponen angka tidak valid" in lower:
        return "Periksa format eksponen, misalnya 1e3 atau 2.5e-2."
    if "ketangkep" in lower or "akhirnya" in lower:
        return "Pastikan 'ketangkep' dan 'akhirnya' berada di dalam blok 'coba ... selesai coba'."
    if "baris baru" in lower:
        return "Letakkan setiap pernyataan pada baris baru dan periksa penutup blok."
    if "mengharapkan identifier" in lower or "identifier/nama" in lower or "nama variabel" in lower:
        return "Gunakan nama yang diawali huruf atau garis bawah, lalu periksa tanda baca di sekitarnya."
    if "operator" in lower or "ekspresi" in lower:
        return "Periksa nilai di sekitar operator dan bandingkan bentuknya dengan contoh di SPEC.md."
    if "assignment" in lower or "pemanggilan" in lower:
        return "Gunakan assignment ke variabel yang sudah dibuat atau panggil fungsi dengan tanda kurung."
    if "token tidak cocok" in lower or "token tidak sesuai" in lower:
        return "Periksa keyword yang diharapkan, tanda kurung, koma, dan penutup blok."
    return "Periksa struktur pernyataan dan contoh sintaks di SPEC.md; koreksi bagian yang ditunjuk lalu jalankan --check lagi."


def format_diagnostic(source, filename, line, column, message):
    """Format a precise, actionable diagnostic in Indonesian."""
    lines = source.splitlines()
    line = max(1, int(line or 1))
    column = max(1, int(column or 1))
    snippet = lines[line - 1] if line <= len(lines) else ""
    # Expand tabs in both the source and caret prefix so the pointer remains aligned.
    shown = snippet.expandtabs(4)
    prefix = snippet[:max(0, min(column - 1, len(snippet)))].expandtabs(4)
    pointer = "  " + " " * len(prefix) + "^"
    suggestion = _diagnostic_suggestion(message)
    return (
        f"[{filename}] Baris {line}, kolom {column}: Kesalahan sintaks: {message}\n"
        f"  {shown}\n{pointer}\n"
        f"Saran: {suggestion}"
    )


def _lexer_location(message):
    match = re.search(r"Baris (\d+), kolom (\d+):\s*(.*)", message)
    if match:
        return int(match.group(1)), int(match.group(2)), match.group(3)
    return 1, 1, message


class Parser:
    def __init__(self, source_or_tokens, filename="<string>"):
        self.source = source_or_tokens if isinstance(source_or_tokens, str) else ""
        self.filename = str(filename)
        self.tokens = (
            lex(source_or_tokens)
            if isinstance(source_or_tokens, str)
            else source_or_tokens
        )
        self.i = 0

    @property
    def tok(self):
        return self.tokens[min(self.i, len(self.tokens) - 1)]

    def at(self, value=None, kind=None):
        t = self.tok
        return (value is None or t.value == value) and (
            kind is None or t.kind == kind
        )

    def take(self):
        t = self.tok
        if t.kind != "EOF":
            self.i += 1
        return t

    def fail(self, message):
        if message.startswith("token tidak sesuai"):
            message = message.replace("token tidak sesuai", "token tidak cocok", 1)
        elif message.startswith("harus ada baris baru"):
            message = "Pernyataan berikut harus dimulai pada baris baru."
        raise ParserError(format_diagnostic(
            self.source, self.filename, self.tok.line, self.tok.column, message
        ))

    def need(self, value=None, kind=None):
        if not self.at(value, kind):
            if value is not None:
                expected = repr(value)
            elif kind == "IDENT":
                expected = "identifier/nama"
            elif kind is not None:
                expected = kind
            else:
                expected = "nilai yang valid"
            self.fail(
                f"mengharapkan {expected}, tetapi menemukan {self.tok.value!r}"
            )
        return self.take()

    def skip_lines(self):
        while self.at(kind="NEWLINE"):
            self.take()

    def name(self):
        return self.need(kind="IDENT").value

    def parse(self):
        self.skip_lines()
        self.need("jancuk")
        self.skip_lines()
        body = self.statements({("selesai", "jancuk")})
        self.need("selesai")
        self.need("jancuk")
        self.skip_lines()
        self.need(kind="EOF")
        return node("Program", body[0].line if body else 1, body=body)

    def statements(self, stops):
        result = []
        self.skip_lines()
        while not self.at(kind="EOF"):
            if any(self.at(v) for v, _ in stops):
                break
            start = self.tok
            result.append(self.statement())
            if self.at(kind="NEWLINE"):
                self.skip_lines()
            elif not self.at(kind="EOF") and not any(
                self.at(v) for v, _ in stops
            ):
                self.fail("harus ada baris baru setelah pernyataan")
            if self.tok is start:
                self.fail("parser tidak dapat melanjutkan")
        return result

    def statement(self):
        t = self.tok
        if self.at("lah"):
            self.take()
            name = self.name()
            self.need("=")
            return node("Declare", t.line, name=name, value=self.expr())
        if self.at("hedeh"):
            self.take()
            return node("Print", t.line, value=self.expr())
        if self.at("tanya"):
            self.take()
            name = self.name()
            self.need("=")
            return node("Input", t.line, name=name, prompt=self.expr())
        if self.at("coba"):
            self.take()
            self.skip_lines()
            body = self.statements({("ketangkep", None), ("akhirnya", None), ("selesai", None)})
            handler_name = None
            handler = []
            final = []
            if self.at("ketangkep"):
                self.take()
                handler_name = self.name()
                self.skip_lines()
                handler = self.statements({("akhirnya", None), ("selesai", None)})
            if self.at("akhirnya"):
                self.take()
                self.skip_lines()
                final = self.statements({("selesai", None)})
            self.need("selesai")
            self.need("coba")
            return node("Try", t.line, body=body, handler_name=handler_name, handler=handler, final=final)
        if self.at("akhirnya") or self.at("ketangkep"):
            self.fail("akhirnya/ketangkep harus berada di dalam blok coba")
        if self.at("njir"):
            self.take()
            condition = self.expr()
            self.skip_lines()
            yes = self.statements({("kampret", None), ("selesai", None)})
            no = []
            if self.at("kampret"):
                self.take()
                self.skip_lines()
                no = self.statements({("selesai", None)})
            self.need("selesai")
            self.need("njir")
            return node("If", t.line, condition=condition,
                        then_body=yes, else_body=no)
        if self.at("mumet"):
            self.take()
            condition = self.expr()
            self.skip_lines()
            body = self.statements({("selesai", None)})
            self.need("selesai")
            self.need("mumet")
            return node("While", t.line, condition=condition, body=body)
        if self.at("untuk"):
            self.take()
            name = self.name()
            self.need("dalam")
            iterable = self.expr()
            self.skip_lines()
            body = self.statements({("selesai", None)})
            self.need("selesai")
            self.need("untuk")
            return node("For", t.line, name=name, iterable=iterable, body=body)
        if self.at("fungsi"):
            self.take()
            name = self.name()
            self.need("(")
            params = []
            if not self.at(")"):
                params.append(self.name())
                while self.at(","):
                    self.take()
                    params.append(self.name())
            self.need(")")
            self.skip_lines()
            body = self.statements({("selesai", None)})
            self.need("selesai")
            self.need("fungsi")
            return node("Function", t.line, name=name,
                        params=params, body=body)
        if self.at("balek"):
            self.take()
            if self.at(kind="NEWLINE") or self.at(kind="EOF"):
                self.fail("balek butuh ekspresi")
            value = self.expr()
            return node("Return", t.line, value=value)
        if self.at(kind="IDENT"):
            name = self.take().value
            if self.at("("):
                return self.call(name, t.line)
            if name in ("tulis", "angkut"):
                args = [self.expr()]
                while self.at(","):
                    self.take()
                    args.append(self.expr())
                return node("Call", t.line, name=name, args=args)

            target = node("Variable", t.line, name=name)
            while self.at("["):
                self.take()
                index = self.expr()
                self.need("]")
                target = node("Index", t.line,
                              collection=target, index=index)

            if self.at("="):
                self.take()
                value = self.expr()
                if target.kind == "Variable":
                    return node("Assign", t.line,
                                name=name, value=value)
                return node("IndexAssign", t.line,
                            collection=target.collection,
                            index=target.index, value=value)

            self.fail("identifier harus berupa assignment atau pemanggilan")
        self.fail(f"pernyataan tidak dikenal: {t.value!r}")

    PRECEDENCE = {
        "atau": 1, "dan": 2,
        "==": 3, "!=": 3, "<": 3, "<=": 3, ">": 3, ">=": 3,
        "+": 4, "-": 4,
        "*": 5, "/": 5, "//": 5, "%": 5,
    }

    def expr(self, minimum=0):
        t = self.take()
        if t.kind in ("INTEGER", "FLOAT", "STRING"):
            left = node("Literal", t.line, value=t.value)
        elif t.kind == "IDENT":
            if self.at("."):
                self.take()
                member = self.name()
                if self.at("("):
                    left = self.call(t.value + "." + member, t.line)
                else:
                    left = node("Attribute", t.line, object=node("Variable", t.line, name=t.value), name=member)
            elif self.at("("):
                left = self.call(t.value, t.line)
            elif t.value in ("baca", "angkut", "kepo_internet"):
                left = node("Call", t.line, name=t.value, args=[self.expr(6)])
            else:
                left = node("Variable", t.line, name=t.value)
        elif t.value == "tanya":
            if self.at("("):
                left = self.call("tanya", t.line)
            else:
                left = node("Call", t.line, name="tanya", args=[self.expr(6)])
        elif t.value in ("benar", "salah"):
            left = node("Literal", t.line, value=(t.value == "benar"))
        elif t.value == "bukan":
            left = node("Unary", t.line, op="bukan", value=self.expr(6))
        elif t.value == "-":
            left = node("Unary", t.line, op="-", value=self.expr(6))
        elif t.value == "(":
            left = self.expr()
            self.need(")")
        elif t.value == "[":
            items = []
            if not self.at("]"):
                items.append(self.expr())
                while self.at(","):
                    self.take()
                    if self.at("]"):
                        break
                    items.append(self.expr())
            self.need("]")
            left = node("List", t.line, items=items)
        elif t.value == "{":
            items = []
            if not self.at("}"):
                while True:
                    key = self.expr()
                    self.need(":")
                    value = self.expr()
                    items.append((key, value))
                    if not self.at(","):
                        break
                    self.take()
                    if self.at("}"):
                        break
            self.need("}")
            left = node("Dict", t.line, items=items)
        else:
            message = f"ekspresi tidak valid: {t.value!r}"
            raise ParserError(format_diagnostic(
                self.source, self.filename, t.line, t.column, message
            ))

        while True:
            if self.at("["):
                bracket = self.take()
                index = self.expr()
                self.need("]")
                left = node("Index", bracket.line,
                            collection=left, index=index)
                continue

            op = self.tok.value
            precedence = self.PRECEDENCE.get(op, -1)
            if precedence < minimum:
                break
            ot = self.take()
            right = self.expr(precedence + 1)
            left = node("Binary", ot.line, op=op, left=left, right=right)
        return left

    def call(self, name, line):
        self.need("(")
        args = []
        if not self.at(")"):
            args.append(self.expr())
            while self.at(","):
                self.take()
                args.append(self.expr())
        self.need(")")
        return node("Call", line, name=name, args=args)


def parse(source, filename="<string>"):
    try:
        return Parser(source, filename=filename).parse()
    except LexerError as exc:
        line, column, message = _lexer_location(str(exc))
        raise ParserError(format_diagnostic(
            source, filename, line, column,
            "kesalahan lexer: " + message
        )) from exc
