"""Portable C11 source backend for the explicitly supported integer/boolean subset."""
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
    if (a == INT64_MIN && b == -1) return 0;
    int64_t remainder = a % b;
    if (remainder != 0 && ((remainder < 0) != (b < 0))) remainder += b;
    return remainder;
}
'''


SUPPORTED_NODES = {
    "Program", "Declare", "Assign", "Print", "If",
    "Literal", "Variable", "Unary", "Binary",
}


def _node(kind, fields, line):
    if not isinstance(fields, dict) or not isinstance(line, int):
        raise CBackendError("node IR tidak valid")
    if kind not in SUPPORTED_NODES:
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

    next_id = 0

    def expression(n, names, types):
        kind, fields, line = n.get("kind"), n.get("fields"), n.get("line")
        _node(kind, fields, line)

        if kind == "Literal":
            value = fields.get("value")
            if type(value) is bool:
                return ("INT64_C(1)" if value else "INT64_C(0)", "bool")
            if type(value) is int and 0 <= value <= 9223372036854775807:
                return (f"INT64_C({value})", "int")
            raise CBackendError(
                f"baris {line}: backend C hanya mendukung literal integer nonnegatif "
                "sampai INT64_MAX dan boolean benar/salah"
            )

        if kind == "Variable":
            name = fields.get("name")
            if name not in names:
                raise CBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
            return names[name], types[name]

        if kind == "Unary":
            value, value_type = expression(fields.get("value"), names, types)
            op = fields.get("op")
            if op == "-":
                if value_type != "int":
                    raise CBackendError(f"baris {line}: unary minus hanya mendukung integer")
                return f"pc_sub(INT64_C(0), ({value}))", "int"
            if op == "bukan":
                return f"(!({value}))", "bool"
            raise CBackendError(f"baris {line}: operator unary {op!r} belum didukung")

        if kind == "Binary":
            op = fields.get("op")
            left, left_type = expression(fields.get("left"), names, types)
            right, right_type = expression(fields.get("right"), names, types)

            if op in {"+", "-", "*", "//", "%"}:
                if left_type != "int" or right_type != "int":
                    raise CBackendError(f"baris {line}: operator {op!r} hanya mendukung operand integer")
                helper = {
                    "+": "pc_add", "-": "pc_sub", "*": "pc_mul",
                    "//": "pc_floor_div", "%": "pc_mod",
                }[op]
                return f"{helper}(({left}), ({right}))", "int"

            if op in {"dan", "atau"}:
                operator = "&&" if op == "dan" else "||"
                # C's logical operators preserve the language's short-circuit behavior.
                return f"((({left}) != 0) {operator} (({right}) != 0))", "bool"

            if op in {"==", "!="}:
                if left_type != right_type:
                    return ("INT64_C(0)" if op == "==" else "INT64_C(1)", "bool")
                operator = "==" if op == "==" else "!="
                return f"(({left}) {operator} ({right}))", "bool"

            if op in {"<", "<=", ">", ">="}:
                operator = op
                return f"(({left}) {operator} ({right}))", "bool"

            raise CBackendError(f"baris {line}: operator {op!r} belum didukung backend C")

        raise CBackendError(f"baris {line}: ekspresi {kind!r} belum didukung backend C")

    def statements(nodes, names, types, indent="    "):
        nonlocal next_id
        lines = []
        for statement in nodes:
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
                value, value_type = expression(fields.get("value"), names, types)
                c_name = f"pc_v_{next_id}"
                next_id += 1
                names[name] = c_name
                types[name] = value_type
                lines.append(f"{indent}int64_t {c_name} = (int64_t)({value});")
                # Keep -Wextra -Werror builds clean for intentionally unused declarations.
                lines.append(f"{indent}(void){c_name};")

            elif kind == "Assign":
                name = fields.get("name")
                if name not in names:
                    raise CBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
                value, value_type = expression(fields.get("value"), names, types)
                if value_type != types[name]:
                    raise CBackendError(
                        f"baris {line}: backend C subset tidak mendukung perubahan tipe "
                        f"variabel {name!r} dari {types[name]} ke {value_type}"
                    )
                lines.append(f"{indent}{names[name]} = (int64_t)({value});")

            elif kind == "Print":
                value, value_type = expression(fields.get("value"), names, types)
                if value_type == "bool":
                    lines.append(
                        f'{indent}if (printf("%s\\n", ({value}) ? "okelah" : "tidak") < 0) '
                        "return EXIT_FAILURE;"
                    )
                else:
                    lines.append(
                        f'{indent}if (printf("%" PRId64 "\\n", (int64_t)({value})) < 0) '
                        "return EXIT_FAILURE;"
                    )

            elif kind == "If":
                condition, _condition_type = expression(fields.get("condition"), names, types)
                lines.append(f"{indent}if (({condition}) != 0) {{")
                then_lines = statements(
                    fields.get("then_body", []), dict(names), dict(types), indent + "    "
                )
                lines.extend(then_lines or [indent + "    (void)0;"])
                else_body = fields.get("else_body", [])
                if else_body:
                    lines.append(f"{indent}}} else {{")
                    else_lines = statements(
                        else_body, dict(names), dict(types), indent + "    "
                    )
                    lines.extend(else_lines or [indent + "    (void)0;"])
                lines.append(f"{indent}}}")

            else:
                raise CBackendError(f"baris {line}: pernyataan {kind!r} belum didukung backend C")

        return lines

    lines = statements(body, {}, {})
    body_text = "\n".join(lines) if lines else "    (void)0;"
    return C_RUNTIME + "\nint main(void) {\n" + body_text + "\n    return EXIT_SUCCESS;\n}\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Kompilasi subset integer/boolean Pusingcuk menjadi source C11."
    )
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
