"""Experimental standalone Rust backend for PusingCuk's numeric core subset."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from compiler.ir import from_source, validate


class RustBackendError(ValueError):
    """Source construct is outside the explicitly supported Rust subset."""


RUNTIME = r'''fn pc_num(value: f64) -> f64 {
    if !value.is_finite() { panic!("PusingCuk Rust: hasil angka non-finite"); }
    value
}
fn pc_div(a: f64, b: f64) -> f64 {
    if b == 0.0 { panic!("PusingCuk Rust: pembagian dengan nol"); }
    pc_num(a / b)
}
fn pc_floor_div(a: f64, b: f64) -> f64 {
    if b == 0.0 { panic!("PusingCuk Rust: pembagian dengan nol"); }
    pc_num((a / b).floor())
}
fn pc_mod(a: f64, b: f64) -> f64 {
    if b == 0.0 { panic!("PusingCuk Rust: modulo dengan nol"); }
    pc_num(a - (a / b).floor() * b)
}
fn pc_out(value: f64) {
    if !value.is_finite() { panic!("PusingCuk Rust: output angka non-finite"); }
    if value.fract() == 0.0 { println!("{:.0}", value); }
    else { println!("{}", value); }
}
'''


def _number(value, line):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RustBackendError(f"baris {line}: backend Rust tahap awal hanya mendukung literal angka")
    text = repr(float(value))
    if "." not in text and "e" not in text.lower():
        text += ".0"
    return text


def generate(document: dict) -> str:
    validate(document)
    root = document["program"]
    if root["kind"] != "Program":
        raise RustBackendError("IR root must be Program")
    env = {}
    lines = [RUNTIME, "", "fn main() {"]
    indent = "    "

    def expr(node):
        kind, fields, line = node["kind"], node["fields"], node["line"]
        if kind == "Literal":
            return _number(fields["value"], line)
        if kind == "Variable":
            name = fields["name"]
            if name not in env:
                raise RustBackendError(f"baris {line}: variabel belum dideklarasikan: {name}")
            return env[name]
        if kind == "Unary" and fields["op"] == "-":
            return f"pc_num(-({expr(fields['value'])}))"
        if kind == "Binary":
            op = fields["op"]
            left, right = expr(fields["left"]), expr(fields["right"])
            if op == "+": return f"pc_num(({left}) + ({right}))"
            if op == "-": return f"pc_num(({left}) - ({right}))"
            if op == "*": return f"pc_num(({left}) * ({right}))"
            if op == "/": return f"pc_div(({left}), ({right}))"
            if op == "//": return f"pc_floor_div(({left}), ({right}))"
            if op == "%": return f"pc_mod(({left}), ({right}))"
        raise RustBackendError(f"baris {line}: ekspresi belum didukung backend Rust subset: {kind}")

    for statement in root["fields"]["body"]:
        kind, fields, line = statement["kind"], statement["fields"], statement["line"]
        if kind == "Declare":
            name = fields["name"]
            if name in env:
                raise RustBackendError(f"baris {line}: variabel sudah dideklarasikan: {name}")
            target_name = "pc_v_" + name
            value = expr(fields["value"])
            env[name] = target_name
            lines.append(f"{indent}let mut {target_name}: f64 = {value};")
        elif kind == "Assign":
            name = fields["name"]
            if name not in env:
                raise RustBackendError(f"baris {line}: variabel belum dideklarasikan: {name}")
            lines.append(f"{indent}{env[name]} = {expr(fields['value'])};")
        elif kind == "Print":
            lines.append(f"{indent}pc_out({expr(fields['value'])});")
        else:
            raise RustBackendError(f"baris {line}: statement belum didukung backend Rust subset: {kind}")

    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="PusingCuk Rust subset backend")
    parser.add_argument("file")
    parser.add_argument("-o", "--output")
    args = parser.parse_args(argv)
    path = Path(args.file)
    try:
        source = path.read_text(encoding="utf-8")
        generated = generate(from_source(source, path.name))
        if args.output:
            Path(args.output).write_text(generated, encoding="utf-8")
        else:
            sys.stdout.write(generated)
    except (OSError, SyntaxError, ValueError, TypeError) as exc:
        print(f"kompilasi gagal: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
