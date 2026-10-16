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
LANGUAGE_VERSION = "0.5-dev"
NODE_KINDS = {
    "Program", "Declare", "Print", "Input", "If", "While", "For",
    "Function", "Return", "Assign", "IndexAssign", "Variable", "Literal", "Try",
    "Unary", "Binary", "List", "Dict", "Index", "Call",
}
FEATURE_RULES = {
    "Input": "console-input", "If": "control-flow", "While": "control-flow",
    "For": "control-flow", "Function": "functions", "Return": "functions",
    "List": "lists", "Dict": "dictionaries", "Index": "indexing",
    "IndexAssign": "indexing", "Call": "calls", "Unary": "operators",
    "Binary": "operators", "Try": "error-handling", "Declare": "variables", "Assign": "variables",
    "Variable": "variables", "Print": "console-output",
}
ENVELOPE_KEYS = {
    "format", "ir_version", "language_version", "source_name",
    "features", "source_map", "program",
}

# Resource limits apply to generated and externally supplied IR documents.
MAX_IR_BYTES = 8 * 1024 * 1024
MAX_DEPTH = 128
MAX_NODES = 100_000
MAX_COLLECTION_ITEMS = 100_000
MAX_STRING_CHARS = 1_000_000

NODE_FIELDS = {
    "Program": {"body"},
    "Declare": {"name", "value"},
    "Print": {"value"},
    "Input": {"name", "prompt"},
    "If": {"condition", "then_body", "else_body"},
    "While": {"condition", "body"},
    "For": {"name", "iterable", "body"},
    "Function": {"name", "params", "body"},
    "Return": {"value"},
    "Assign": {"name", "value"},
    "IndexAssign": {"collection", "index", "value"},
    "Variable": {"name"},
    "Literal": {"value"},
    "Unary": {"op", "value"},
    "Binary": {"op", "left", "right"},
    "List": {"items"},
    "Dict": {"items"},
    "Index": {"collection", "index"},
    "Call": {"name", "args"},
    "Try": {"body", "handler_name", "handler", "final"},
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
    stack = [program]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            kind = value.get("kind")
            if kind in FEATURE_RULES:
                found.add(FEATURE_RULES[kind])
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
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
        "source_name": Path(source_name.replace(chr(92), "/")).name if source_name != "<memory>" else source_name,
        "features": _features(program),
        "source_map": source_map,
        "program": program,
    }
    validate(document)
    return document


def _validate_value(value: Any, path: str, *, depth: int = 0,
                    node_counter: list[int] | None = None) -> None:
    if depth > MAX_DEPTH:
        raise IRValidationError(f"kedalaman IR melewati batas {MAX_DEPTH} pada {path}")
    if value is None or isinstance(value, (bool, int)): return
    if isinstance(value, str):
        if len(value) > MAX_STRING_CHARS: raise IRValidationError(f"teks melewati batas {MAX_STRING_CHARS} karakter pada {path}")
        return
    if isinstance(value, float):
        if not math.isfinite(value): raise IRValidationError(f"angka non-finite tidak valid pada {path}")
        return
    if isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS: raise IRValidationError(f"koleksi melewati batas {MAX_COLLECTION_ITEMS} item pada {path}")
        for index, item in enumerate(value): _validate_value(item, f"{path}[{index}]", depth=depth + 1, node_counter=node_counter)
        return
    if isinstance(value, dict):
        if len(value) > MAX_COLLECTION_ITEMS: raise IRValidationError(f"objek melewati batas {MAX_COLLECTION_ITEMS} field pada {path}")
        if "kind" in value:
            if set(value) != {"kind", "line", "fields"}: raise IRValidationError(f"node tidak memiliki field tepat pada {path}")
            kind, line, fields = value["kind"], value["line"], value["fields"]
            if not isinstance(kind, str) or kind not in NODE_KINDS: raise IRValidationError(f"jenis node tidak dikenal pada {path}: {kind!r}")
            if not isinstance(line, int) or isinstance(line, bool) or line < 1: raise IRValidationError(f"baris node tidak valid pada {path}")
            if not isinstance(fields, dict): raise IRValidationError(f"fields node harus objek pada {path}")
            if set(fields) != NODE_FIELDS[kind]:
                raise IRValidationError(f"field node {kind} tidak cocok pada {path}: diharapkan {sorted(NODE_FIELDS[kind])}, ditemukan {sorted(fields)}")
            if node_counter is not None:
                node_counter[0] += 1
                if node_counter[0] > MAX_NODES: raise IRValidationError(f"jumlah node IR melewati batas {MAX_NODES}")
            for key, item in fields.items(): _validate_value(item, f"{path}.fields.{key}", depth=depth + 1, node_counter=node_counter)
            return
        for key, item in value.items():
            if not isinstance(key, str): raise IRValidationError(f"kunci objek harus teks pada {path}")
            _validate_value(item, f"{path}.{key}", depth=depth + 1, node_counter=node_counter)
        return
    raise IRValidationError(f"tipe nilai tidak didukung pada {path}: {type(value).__name__}")


def _collect_node_locations(program: dict) -> list[dict]:
    """Return node paths/lines in deterministic serialization order."""
    locations, stack = [], [("$", program)]
    while stack:
        path, value = stack.pop()
        if isinstance(value, dict):
            if "kind" in value:
                locations.append({"path": path, "line": value["line"]})
                fields = value.get("fields", {})
                stack.extend(reversed([(f"{path}.fields.{key}", fields[key]) for key in sorted(fields)]))
            else:
                stack.extend(reversed([(f"{path}.{key}", value[key]) for key in sorted(value)]))
        elif isinstance(value, list):
            stack.extend(reversed([(f"{path}[{i}]", child) for i, child in enumerate(value)]))
    return locations


def validate(document: Any) -> dict:
    """Validate IR v1 without executing it; return the original document."""
    if not isinstance(document, dict) or set(document) != ENVELOPE_KEYS: raise IRValidationError("envelope IR harus memiliki field yang ditentukan")
    if document["format"] != FORMAT: raise IRValidationError("format artefak bukan pusingcuk-ir")
    if type(document["ir_version"]) is not int or document["ir_version"] != IR_VERSION: raise IRValidationError(f"versi IR tidak didukung; diperlukan {IR_VERSION}")
    if not isinstance(document["language_version"], str) or not document["language_version"]: raise IRValidationError("language_version harus berupa teks nonkosong")
    if not isinstance(document["source_name"], str) or not document["source_name"]: raise IRValidationError("source_name harus berupa teks nonkosong")
    if "/" in document["source_name"] or chr(92) in document["source_name"] or document["source_name"] in {".", ".."}: raise IRValidationError("source_name harus berupa nama file, bukan path")
    features = document["features"]
    if not isinstance(features, list) or any(not isinstance(x, str) or not x for x in features): raise IRValidationError("features harus berupa daftar teks nonkosong")
    if features != sorted(set(features)): raise IRValidationError("features harus unik dan terurut")
    source_map = document["source_map"]
    if not isinstance(source_map, list): raise IRValidationError("source_map harus berupa daftar")
    if len(source_map) > MAX_NODES: raise IRValidationError(f"source_map melewati batas {MAX_NODES} entri")
    seen_paths = set()
    for entry in source_map:
        if not isinstance(entry, dict) or set(entry) != {"path", "line"}: raise IRValidationError("setiap source_map entry harus memiliki path dan line")
        if not isinstance(entry["path"], str) or not entry["path"].startswith("$"): raise IRValidationError("source_map.path tidak valid")
        if entry["path"] in seen_paths: raise IRValidationError("source_map.path duplikat")
        seen_paths.add(entry["path"])
        if not isinstance(entry["line"], int) or isinstance(entry["line"], bool) or entry["line"] < 1: raise IRValidationError("source_map.line harus integer positif")
    node_counter = [0]
    _validate_value(document["program"], "$.program", node_counter=node_counter)
    if not isinstance(document["program"], dict) or document["program"].get("kind") != "Program": raise IRValidationError("root program harus node Program")
    if document["features"] != _features(document["program"]): raise IRValidationError("features tidak cocok dengan node program")
    if source_map != _collect_node_locations(document["program"]): raise IRValidationError("source_map tidak cocok dengan lokasi node pada program")
    return document

def dumps(document: dict) -> str:
    validate(document)
    return json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def loads(text: str) -> dict:
    if not isinstance(text, str): raise IRValidationError("dokumen IR harus berupa teks JSON")
    if len(text.encode("utf-8")) > MAX_IR_BYTES: raise IRValidationError(f"ukuran IR melewati batas {MAX_IR_BYTES} byte")
    try:
        document = json.loads(text, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
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
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError) as exc:
        print(f"Kesalahan IR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
