#!/usr/bin/env python3
# LEGACY - active is compiler/ folder
"""Experimental, versioned JSON AST-IR export for Pusingcuk."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from parser import parse

IR_VERSION = 1
LANGUAGE_VERSION = "0.4-dev"
NODE_KINDS = {
    "Program", "Declare", "Print", "Input", "If", "While", "For",
    "Function", "Return", "Assign", "IndexAssign", "Variable",
    "Literal", "List", "Dict", "Index", "Unary", "Binary", "Call",
}
MAX_NODES = 100_000
MAX_DEPTH = 256


class IRValidationError(ValueError):
    """Raised when an IR document does not satisfy the versioned schema."""


def _encode(value, next_id, source_name, source_map, depth):
    if depth > MAX_DEPTH:
        raise IRValidationError("AST terlalu dalam untuk IR v1")
    if hasattr(value, "kind") and hasattr(value, "fields") and hasattr(value, "line"):
        node_id = next_id[0]
        next_id[0] += 1
        if next_id[0] > MAX_NODES:
            raise IRValidationError("jumlah node melampaui batas IR v1")
        line = value.line if isinstance(value.line, int) and value.line > 0 else 1
        source_map.append({"node_id": node_id, "source": source_name, "line": line})
        fields = {
            key: _encode(child, next_id, source_name, source_map, depth + 1)
            for key, child in sorted(value.fields.items())
        }
        return {"node_id": node_id, "kind": value.kind, "line": line, "fields": fields}
    if value is None or isinstance(value, (str, bool, int, float)):
        if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
            raise IRValidationError("nilai angka non-finite tidak diizinkan dalam IR")
        return value
    if isinstance(value, (list, tuple)):
        return [_encode(child, next_id, source_name, source_map, depth + 1) for child in value]
    if isinstance(value, dict):
        return {
            str(key): _encode(child, next_id, source_name, source_map, depth + 1)
            for key, child in sorted(value.items(), key=lambda item: str(item[0]))
        }
    raise IRValidationError(f"jenis nilai AST tidak didukung: {type(value).__name__}")


def lower_to_ir(source_text, source_name="<memory>"):
    """Parse source and serialize it into deterministic, experimental AST IR v1."""
    tree = parse(source_text)
    source_map = []
    program = _encode(tree, [0], source_name, source_map, 0)
    features = sorted({entry["kind"] for entry in walk_nodes(program)})
    document = {
        "format": "pusingcuk-ast-ir",
        "ir_version": IR_VERSION,
        "language_version": LANGUAGE_VERSION,
        "source_name": source_name,
        "features": features,
        "entry_point": "program",
        "program": program,
        "source_map": source_map,
    }
    validate_ir(document)
    return document


def walk_nodes(value):
    if isinstance(value, dict):
        if {"node_id", "kind", "line", "fields"} <= set(value):
            yield value
        for child in value.values():
            yield from walk_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_nodes(child)


def validate_ir(document):
    if not isinstance(document, dict):
        raise IRValidationError("dokumen IR harus berupa objek")
    required = {
        "format", "ir_version", "language_version", "source_name",
        "features", "entry_point", "program", "source_map",
    }
    if set(document) != required:
        raise IRValidationError("field dokumen IR tidak sesuai schema v1")
    if document["format"] != "pusingcuk-ast-ir" or document["ir_version"] != IR_VERSION:
        raise IRValidationError("format atau versi IR tidak didukung")
    if document["language_version"] != LANGUAGE_VERSION:
        raise IRValidationError("versi bahasa tidak didukung oleh validator ini")
    if not isinstance(document["source_name"], str) or not document["source_name"]:
        raise IRValidationError("source_name harus berupa teks tidak kosong")
    if document["entry_point"] != "program":
        raise IRValidationError("entry_point IR v1 harus 'program'")
    if not isinstance(document["features"], list) or any(
        not isinstance(feature, str) for feature in document["features"]
    ):
        raise IRValidationError("features harus berupa daftar teks")
    if not isinstance(document["source_map"], list):
        raise IRValidationError("source_map harus berupa daftar")

    nodes = list(walk_nodes(document["program"]))
    if not nodes or len(nodes) > MAX_NODES:
        raise IRValidationError("program IR kosong atau melampaui batas node")
    ids = set()
    for item in nodes:
        if set(item) != {"node_id", "kind", "line", "fields"}:
            raise IRValidationError("bentuk node IR tidak valid")
        if not isinstance(item["node_id"], int) or isinstance(item["node_id"], bool) or item["node_id"] < 0:
            raise IRValidationError("node_id harus integer nonnegatif")
        if item["node_id"] in ids:
            raise IRValidationError("node_id duplikat")
        ids.add(item["node_id"])
        if item["kind"] not in NODE_KINDS:
            raise IRValidationError(f"jenis node tidak dikenal: {item['kind']!r}")
        if not isinstance(item["line"], int) or isinstance(item["line"], bool) or item["line"] < 1:
            raise IRValidationError("line node harus integer positif")
        if not isinstance(item["fields"], dict):
            raise IRValidationError("fields node harus berupa objek")

    expected_map = [
        {"node_id": item["node_id"], "source": document["source_name"], "line": item["line"]}
        for item in nodes
    ]
    if document["source_map"] != expected_map:
        raise IRValidationError("source_map tidak cocok dengan node program")
    expected_features = sorted({item["kind"] for item in nodes})
    if document["features"] != expected_features:
        raise IRValidationError("features tidak cocok dengan node program")
    return document


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ekspor sumber Pusingcuk menjadi artefak JSON AST-IR eksperimental."
    )
    parser.add_argument("file", help="berkas sumber .pusingcuk")
    parser.add_argument("-o", "--output", help="tujuan JSON; default stdout")
    args = parser.parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        print(f"Kesalahan: berkas tidak ditemukan: {path}", file=sys.stderr)
        return 2
    try:
        document = lower_to_ir(path.read_text(encoding="utf-8"), str(path))
        output = json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
    except (SyntaxError, ValueError, TypeError, OSError) as exc:
        print(f"Kesalahan: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
