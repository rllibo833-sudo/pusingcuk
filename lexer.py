"""Lexer untuk bahasa Pusingcuk 0.6-dev (metadata paket main: 0.8.0.dev0)."""

from dataclasses import dataclass


KEYWORD_ALIASES = {
    "jir": "hedeh",
    "adooh": "kampret",
    "gitu": "selesai",
    "inthiseco": "jancuk",
    "janggal": "bukan",
    "gas": "jancuk",
    "spill": "hedeh",
    "bestie": "lah",
    "valid": "benar",
    "zonk": "salah",
    "skip": "kampret",
    "kelar": "selesai",
    "simpen": "tulis",
    "bongkar": "baca",
    "simpen_json": "tulis_json",
    "bongkar_json": "baca_json",
    "impor": "angkut",
    "waktu": "jam",
    "gas_api": "kepo_internet",
    "stalking": "kepo_internet",
    "kirim_gosip": "kirim_api",
    "parse_json": "jadi_json",
    "kepo": "tanya",
}

KEYWORDS = frozenset({
    "jancuk",
    "selesai",
    "lah",
    "hedeh",
    "njir",
    "kampret",
    "mumet",
    "untuk",
    "dalam",
    "tanya",
    "fungsi",
    "balek",
    "dan",
    "atau",
    "bukan",
    "benar",
    "salah",
    "coba",
    "ketangkep",
    "akhirnya",
}) | frozenset(KEYWORD_ALIASES)

MULTI_OPERATORS = ("==", "!=", "<=", ">=", "//")
SINGLE_OPERATORS = frozenset("+-*/%=<>")
PUNCTUATION = frozenset("()[],:{}.")


class LexerError(ValueError):
    """Kesalahan ketika membaca karakter sumber."""


@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int

    def __repr__(self):
        return (
            f"Token({self.kind!r}, {self.value!r}, "
            f"baris={self.line}, kolom={self.column})"
        )


def _is_ascii_digit(char: str) -> bool:
    """Accept only ASCII decimal digits as numeric literal characters."""
    return len(char) == 1 and "0" <= char <= "9"


class Lexer:
    def __init__(self, source):
        if not isinstance(source, str):
            raise TypeError("Sumber lexer harus berupa string.")

        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.length = len(source)

    def _peek(self, offset=0):
        index = self.position + offset
        if index >= self.length:
            return ""
        return self.source[index]

    def _advance(self):
        char = self._peek()
        if not char:
            return ""

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def _error(self, line, column, message):
        raise LexerError(
            f"Baris {line}, kolom {column}: {message}"
        )

    def _read_number(self):
        line, column = self.line, self.column
        start = self.position

        while _is_ascii_digit(self._peek()):
            self._advance()

        kind = "INTEGER"

        if self._peek() == "." and _is_ascii_digit(self._peek(1)):
            kind = "FLOAT"
            self._advance()

            while _is_ascii_digit(self._peek()):
                self._advance()

        if self._peek() in ("e", "E"):
            kind = "FLOAT"
            self._advance()

            if self._peek() in ("+", "-"):
                self._advance()

            if not _is_ascii_digit(self._peek()):
                self._error(
                    line,
                    max(1, self.column - 1),
                    "eksponen angka tidak valid",
                )

            while _is_ascii_digit(self._peek()):
                self._advance()

        text = self.source[start:self.position]

        if kind == "INTEGER":
            value = int(text)
        else:
            value = float(text)

        return Token(kind, value, line, column)

    def _read_identifier(self):
        line, column = self.line, self.column
        start = self.position

        self._advance()

        while True:
            char = self._peek()
            if not char or not (
                char.isascii() and (char.isalnum() or char == "_")
            ):
                break
            self._advance()

        value = self.source[start:self.position]
        value = KEYWORD_ALIASES.get(value, value)
        kind = "KEYWORD" if value in KEYWORDS else "IDENT"

        return Token(kind, value, line, column)

    def _read_string(self):
        line, column = self.line, self.column
        quote = self._advance()
        chars = []

        escapes = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            '"': '"',
            "'": "'",
        }

        while True:
            char = self._peek()

            if not char:
                self._error(
                    line, column, "string belum ditutup"
                )

            if char == "\n":
                self._error(
                    line, column,
                    "string tidak boleh melewati baris tanpa escape"
                )

            self._advance()

            if char == quote:
                break

            if char == "\\":
                escaped = self._peek()

                if not escaped:
                    self._error(
                        line, column, "escape string tidak lengkap"
                    )

                if escaped == "\n":
                    self._error(
                        self.line, self.column,
                        "escape baris baru belum didukung"
                    )

                self._advance()

                if escaped not in escapes:
                    self._error(
                        self.line,
                        max(1, self.column - 1),
                        f"escape tidak dikenal: \\{escaped}",
                    )

                chars.append(escapes[escaped])
            else:
                chars.append(char)

        return Token("STRING", "".join(chars), line, column)

    def tokenize(self):
        tokens = []

        while self.position < self.length:
            char = self._peek()

            if char in " \t\r":
                self._advance()
                continue

            if char == "\n":
                tokens.append(
                    Token("NEWLINE", "\n", self.line, self.column)
                )
                self._advance()
                continue

            if char == "#":
                while self._peek() and self._peek() != "\n":
                    self._advance()
                continue

            if char in ("'", '"'):
                tokens.append(self._read_string())
                continue

            if _is_ascii_digit(char):
                tokens.append(self._read_number())
                continue

            if char.isascii() and (
                char.isalpha() or char == "_"
            ):
                tokens.append(self._read_identifier())
                continue

            matched = False

            for operator in MULTI_OPERATORS:
                if self.source.startswith(
                    operator, self.position
                ):
                    line, column = self.line, self.column

                    for _ in operator:
                        self._advance()

                    tokens.append(
                        Token("OP", operator, line, column)
                    )
                    matched = True
                    break

            if matched:
                continue

            if char in SINGLE_OPERATORS:
                tokens.append(
                    Token("OP", char, self.line, self.column)
                )
                self._advance()
                continue

            if char in PUNCTUATION:
                tokens.append(
                    Token("PUNCT", char, self.line, self.column)
                )
                self._advance()
                continue

            self._error(
                self.line,
                self.column,
                f"karakter tidak dikenal: {char!r}",
            )

        tokens.append(Token("EOF", None, self.line, self.column))
        return tokens


def lex(source):
    """Fungsi praktis untuk mengubah teks menjadi daftar token."""
    return Lexer(source).tokenize()

# AUTO-GEN ALIASES V6.2
HEDEH_ALIASES = ['bacot', 'bacrit', 'berak', 'berisik', 'cetak', 'crot', 'gas', 'gebber', 'gembor', 'jedor', 'jir', 'keluarin', 'koar', 'muncrat', 'ngegas', 'nyalak', 'omong', 'print', 'sembur', 'semprot', 'senggol', 'spill', 'suarakan', 'tampilkan', 'teriak']
