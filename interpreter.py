"""Kompatibilitas interpreter lama dengan evaluator modular.

Kontrak eksekusi tunggal: sumber .cuk berbentuk teks masuk ke
Evaluator.run_module(source). Evaluator sendiri bertanggung jawab atas
parse dan eksekusi; jangan parse AST di sini lalu mengirim AST ke API teks.
"""
import re

from evaluator import Evaluator
from parser import ParserError


_MAX_EXPRESSION_LENGTH = 10000
_MAX_EXPRESSION_DEPTH = 120


def _validate_legacy_limits(source):
    """Keep the legacy interpreter's resource limits at its public boundary."""
    for line in source.splitlines():
        if len(line) > _MAX_EXPRESSION_LENGTH:
            raise SyntaxError("ekspresi terlalu panjang")
    repeated_prefix = re.compile(r"(?:(?:not|bukan)\\s+){%d,}" % (_MAX_EXPRESSION_DEPTH + 1))
    if repeated_prefix.search(source):
        raise SyntaxError("ekspresi terlalu dalam")


def _legacy_diagnostic(message):
    """Translate modular evaluator diagnostics to stable legacy wording."""
    if "ZeroDivisionError" in message:
        return "pembagian dengan nol"
    if "indeks di luar batas" in message:
        return "indeks daftar di luar batas"
    if "operator '+' membutuhkan" in message:
        return "tipe data tidak cocok"
    match = re.search(r"fungsi '([^']+)' tidak dikenal", message)
    if match:
        return f"fungsi tidak dikenal: '{match.group(1)}'"
    match = re.search(r"variabel '([^']+)' belum dibuat", message)
    if match:
        return f"variabel '{match.group(1)}' belum ada"
    return message


def run(src, filename="<input>"):
    """Run source text through the evaluator's single source-text API."""
    _validate_legacy_limits(src)
    evaluator = Evaluator(source_path=filename if filename != "<input>" else None)
    try:
        return evaluator.run_module(src)
    except ParserError as exc:
        message = str(exc)
        if "string tidak boleh melewati baris" in message or "Kesalahan lexer" in message:
            message = "ekspresi tidak valid"
        raise SyntaxError(message) from exc
    except RuntimeError as exc:
        raise SyntaxError(_legacy_diagnostic(str(exc))) from exc


def main():
    import sys

    src = sys.stdin.read()
    print(run(src))


if __name__ == "__main__":
    main()
