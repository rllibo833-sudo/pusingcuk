"""Versioned, deterministic Pusingcuk interchange IR (AST-preserving v1).

This is a portable front-end artifact, not yet executable bytecode or a backend.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from ast_nodes import Node
from parser import parse

FORMAT = "pusingcuk-ir"
IR_VERSION = 1
LANGUAGE_VERSION = "0.4-dev"
NODE_KINDS = {
    "Program", "Declare", "Print", "Input", "If", "While", "For",
    "Function", "Return", "Assign", "IndexAssign", "Variable", "Literal",
    "Unary", "Binary", "List", "Dict", "Index", "Call",
}
FEATURE_RULES = {
    "Input": "console-input", "If": "control-flow", "While": "control-flow",
    "For": "control-flow", "Function": "functions", "Return": "functions",
    "List": "lists", "Dict": "dictionaries", "Index": "indexing",
    "IndexAssign": "indexing", "Call": "calls", "Unary": "operators",
    "Binary": "operators", "Declare": "variables", "Assign": "variables",
    "Variable": "variables", "Print": "console-output",
}
ENVELOPE_KEYS = {
    "format", "ir_version", "language_version", "source_name",
    "features", "source_map", "program",
}


class IRValidationError(ValueError):
    """IR document does not satisfy the versioned contract."""


def _json_value(value: Any, path: str, source_map: list[dict]) -> Any:
    if isinstance(value, Node):
        node_path = path or "$"
        source_map.append({"path": node_path, "line": value.line})
        return {
            "kind": value.kind,
            "line": value.line,
            "fields": {
                key: _json_value(item, f"{node_path}.fields.{key}", source_map)
                for key, item in sorted(value.fields.items())
            },
        }
    if isinstance(value, tuple):
        return [_json_value(item, f"{path}[{i}]", source_map) for i, item in enumerate(value)]
    if isinstance(value, list):
        return [_json_value(item, f"{path}[{i}]", source_map) for i, item in enumerate(value)]
    if isinstance(value, dict):
        return {
            str(key): _json_value(item, f"{path}.{key}", source_map)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise IRValidationError(f"nilai tidak dapat diserialisasi pada {path}: {type(value).__name__}")


def _features(program: dict) -> list[str]:
    found = {"core"}
    def visit(value):
        if isinstance(value, dict):
            kind = value.get("kind")
            if kind in FEATURE_RULES:
                found.add(FEATURE_RULES[kind])
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(program)
    return sorted(found)


def from_source(source: str, source_name: str = "<memory>") -> dict:
    """Parse source and create deterministic, versioned AST-preserving IR."""
    if not isinstance(source, str):
        raise TypeError("source harus berupa string")
    if not isinstance(source_name, str) or not source_name:
        raise ValueError("source_name tidak boleh kosong")
    tree = parse(source)
    source_map: list[dict] = []
    program = _json_value(tree, "$", source_map)
    document = {
        "format": FORMAT,
        "ir_version": IR_VERSION,
        "language_version": LANGUAGE_VERSION,
        "source_name": Path(source_name).name if source_name != "<memory>" else source_name,
        "features": _features(program),
        "source_map": source_map,
        "program": program,
    }
    validate(document)
    return document


def _validate_value(value: Any, path: str) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise IRValidationError(f"angka non-finite tidak valid pada {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        if "kind" in value:
            if set(value) != {"kind", "line", "fields"}:
                raise IRValidationError(f"node tidak memiliki field tepat pada {path}")
            kind, line, fields = value["kind"], value["line"], value["fields"]
            if not isinstance(kind, str) or kind not in NODE_KINDS:
                raise IRValidationError(f"jenis node tidak dikenal pada {path}: {kind!r}")
            if not isinstance(line, int) or isinstance(line, bool) or line < 1:
                raise IRValidationError(f"baris node tidak valid pada {path}")
            if not isinstance(fields, dict):
                raise IRValidationError(f"fields node harus objek pada {path}")
            for key, item in fields.items():
                if not isinstance(key, str):
                    raise IRValidationError(f"nama field harus teks pada {path}")
                _validate_value(item, f"{path}.fields.{key}")
            return
        for key, item in value.items():
            if not isinstance(key, str):
                raise IRValidationError(f"kunci objek harus teks pada {path}")
            _validate_value(item, f"{path}.{key}")
        return
    raise IRValidationError(f"tipe nilai tidak didukung pada {path}: {type(value).__name__}")


def validate(document: Any) -> dict:
    """Validate IR v1 without executing it; return the original document."""
    if not isinstance(document, dict) or set(document) != ENVELOPE_KEYS:
        raise IRValidationError("envelope IR harus memiliki field yang ditentukan")
    if document["format"] != FORMAT:
        raise IRValidationError("format artefak bukan pusingcuk-ir")
    if type(document["ir_version"]) is not int or document["ir_version"] != IR_VERSION:
        raise IRValidationError(f"versi IR tidak didukung; diperlukan {IR_VERSION}")
    if not isinstance(document["language_version"], str) or not document["language_version"]:
        raise IRValidationError("language_version harus berupa teks nonkosong")
    if not isinstance(document["source_name"], str) or not document["source_name"]:
        raise IRValidationError("source_name harus berupa teks nonkosong")
    features = document["features"]
    if not isinstance(features, list) or any(not isinstance(x, str) for x in features):
        raise IRValidationError("features harus berupa daftar teks")
    if features != sorted(set(features)):
        raise IRValidationError("features harus unik dan terurut")
    source_map = document["source_map"]
    if not isinstance(source_map, list):
        raise IRValidationError("source_map harus berupa daftar")
    seen_paths = set()
    for entry in source_map:
        if not isinstance(entry, dict) or set(entry) != {"path", "line"}:
            raise IRValidationError("setiap source_map entry harus memiliki path dan line")
        if not isinstance(entry["path"], str) or not entry["path"].startswith("$"):
            raise IRValidationError("source_map.path tidak valid")
        if entry["path"] in seen_paths:
            raise IRValidationError("source_map.path duplikat")
        seen_paths.add(entry["path"])
        if not isinstance(entry["line"], int) or isinstance(entry["line"], bool) or entry["line"] < 1:
            raise IRValidationError("source_map.line harus integer positif")
    _validate_value(document["program"], "$.program")
    if document["program"].get("kind") != "Program":
        raise IRValidationError("root program harus node Program")
    if document["features"] != _features(document["program"]):
        raise IRValidationError("features tidak cocok dengan node program")
    return document


def dumps(document: dict) -> str:
    validate(document)
    return json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def loads(text: str) -> dict:
    try:
        document = json.loads(text, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    except (json.JSONDecodeError, ValueError) as exc:
        raise IRValidationError(f"JSON IR tidak valid: {exc}") from exc
    return validate(document)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Buat atau validasi artefak IR Pusingcuk.")
    parser.add_argument("source", nargs="?", help="berkas sumber .pusingcuk")
    parser.add_argument("-o", "--output", help="tujuan IR JSON; default stdout")
    parser.add_argument("--validate-ir", dest="validate_ir", help="validasi artefak IR JSON")
    args = parser.parse_args(argv)
    try:
        if args.validate_ir:
            document = loads(Path(args.validate_ir).read_text(encoding="utf-8"))
            print(f"IR v{document['ir_version']} valid: {document['source_name']}")
            return 0
        if not args.source:
            parser.error("berikan berkas sumber atau --validate-ir")
        path = Path(args.source)
        document = from_source(path.read_text(encoding="utf-8"), path.name)
        output = dumps(document)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"Kesalahan IR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
