"""Portable C11 source backend for the explicitly supported integer subset."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from compiler.ir import from_source, validate


class CBackendError(ValueError):
    """Source uses a feature outside the current C backend subset."""


C_RUNTIME = r'''#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

static void pc_overflow(void) {
    fputs("Pusingcuk C backend: integer overflow\n", stderr);
    exit(EXIT_FAILURE);
}
static void pc_division_by_zero(void) {
    fputs("Pusingcuk C backend: division by zero\n", stderr);
    exit(EXIT_FAILURE);
}
int64_t pc_add(int64_t a, int64_t b) {
    if ((b > 0 && a > INT64_MAX - b) ||
        (b < 0 && a < INT64_MIN - b)) pc_overflow();
    return a + b;
}
int64_t pc_sub(int64_t a, int64_t b) {
    if ((b > 0 && a < INT64_MIN + b) ||
        (b < 0 && a > INT64_MAX + b)) pc_overflow();
    return a - b;
}
int64_t pc_mul(int64_t a, int64_t b) {
    if (a > 0) {
        if ((b > 0 && a > INT64_MAX / b) ||
            (b < 0 && b < INT64_MIN / a)) pc_overflow();
    } else if (a < 0) {
        if ((b > 0 && a < INT64_MIN / b) ||
            (b < 0 && a < INT64_MAX / b)) pc_overflow();
    }
    return a * b;
}
/* Match Python floor-division semantics rather than C's truncation toward zero. */
int64_t pc_floor_div(int64_t a, int64_t b) {
    if (b == 0) pc_division_by_zero();
    if (a == INT64_MIN && b == -1) pc_overflow();
    int64_t quotient = a / b;
    int64_t remainder = a % b;
    if (remainder != 0 && ((remainder < 0) != (b < 0))) quotient--;
    return quotient;
}
/* Match Python modulo semantics; the result has the divisor's sign. */
int64_t pc_mod(int64_t a, int64_t b) {
    if (b == 0) pc_division_by_zero();
    /* C makes INT64_MIN % -1 undefined, while the mathematical result is zero. */
    if (a == INT64_MIN && b == -1) return 0;
    int64_t remainder = a % b;
    if (remainder != 0 && ((remainder < 0) != (b < 0))) remainder += b;
    return remainder;
}
'''


def _node(kind, fields, line):
    if not isinstance(fields, dict) or not isinstance(line, int):
        raise CBackendError("node IR tidak valid")
    if kind not in {"Program", "Declare", "Assign", "Print", "Literal", "Variable", "Unary", "Binary"}:
        raise CBackendError(f"fitur {kind} belum didukung backend C subset")
    return {"kind": kind, "fields": fields, "line": line}


def generate(document: dict) -> str:
    validate(document)
    program = document["program"]
    if program["kind"] != "Program":
        raise CBackendError("root IR harus Program")
    body = program["fields"].get("body")
    if not isinstance(body, list):
        raise CBackendError("Program.body tidak valid")

    names: dict[str, str] = {}
    lines: list[str] = []
    next_id = 0

    def expression(n):
        kind, fields, line = n.get("kind"), n.get("fields"), n.get("line")
        _node(kind, fields, line)
        if kind == "Literal":
            value = fields.get("value")
            if type(value) is not int or value < 0 or value > 9223372036854775807:
                raise CBackendError(f"baris {line}: backend C hanya mendukung literal integer nonnegatif sampai INT64_MAX")
            return f"((int64_t){value})"
        if kind == "Variable":
            name = fields.get("name")
            if name not in names:
                raise CBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
            return names[name]
        if kind == "Unary":
            if fields.get("op") != "-":
                raise CBackendError(f"baris {line}: backend C hanya mendukung unary minus")
            return f"pc_sub(INT64_C(0), {expression(fields.get('value'))})"
        if kind == "Binary":
            op = fields.get("op")
            helper = {
                "+": "pc_add",
                "-": "pc_sub",
                "*": "pc_mul",
                "//": "pc_floor_div",
                "%": "pc_mod",
            }.get(op)
            if not helper:
                raise CBackendError(f"baris {line}: operator {op!r} belum didukung backend C")
            left = expression(fields.get("left"))
            right = expression(fields.get("right"))
            return f"{helper}({left}, {right})"
        raise CBackendError(f"baris {line}: ekspresi {kind!r} belum didukung backend C")

    for statement in body:
        kind = statement.get("kind")
        fields = statement.get("fields")
        line = statement.get("line")
        _node(kind, fields, line)
        if kind == "Declare":
            name = fields.get("name")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                raise CBackendError(f"baris {line}: nama variabel tidak valid")
            if name in names:
                raise CBackendError(f"baris {line}: variabel {name!r} sudah dideklarasikan")
            c_name = f"pc_v_{next_id}"
            next_id += 1
            value = expression(fields.get("value"))
            names[name] = c_name
            lines.append(f"    int64_t {c_name} = {value};")
        elif kind == "Assign":
            name = fields.get("name")
            if name not in names:
                raise CBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
            value = expression(fields.get("value"))
            lines.append(f"    {names[name]} = {value};")
        elif kind == "Print":
            value = expression(fields.get("value"))
            lines.append(f'    if (printf("%" PRId64 "\\n", (int64_t)({value})) < 0) return EXIT_FAILURE;')
        else:
            raise CBackendError(f"baris {line}: pernyataan {kind!r} belum didukung backend C")

    body_text = "\n".join(lines) if lines else "    (void)0;"
    return C_RUNTIME + "\nint main(void) {\n" + body_text + "\n    return EXIT_SUCCESS;\n}\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Kompilasi subset integer Pusingcuk menjadi source C11.")
    parser.add_argument("source", help="berkas sumber .pusingcuk")
    parser.add_argument("-o", "--output", help="berkas source C tujuan; default stdout")
    args = parser.parse_args(argv)
    try:
        source_path = Path(args.source)
        source = source_path.read_text(encoding="utf-8")
        c_source = generate(from_source(source, source_path.name))
        if args.output:
            Path(args.output).write_text(c_source, encoding="utf-8")
        else:
            sys.stdout.write(c_source)
        return 0
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"Kesalahan backend C: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
