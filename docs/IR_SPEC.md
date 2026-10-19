# PusingCuk JSON IR Specification

**Status:** Frozen format v1 for the 0.6-dev language line.  
**Format identifier:** `pusingcuk-ir`  
**Version field:** `ir_version: 1`

This document defines the serialized interchange format emitted by `compiler.ir.from_source()`. The implementation validator remains executable enforcement; changes to this document and validator must land together with fixtures.

## Envelope

A v1 document has exactly these top-level keys:

- `format`: string `pusingcuk-ir`
- `ir_version`: integer `1` (booleans are not integers for validation)
- `language_version`: language version string, currently `0.6-dev`
- `source_name`: basename or `<memory>`
- `features`: sorted, unique feature-name strings
- `source_map`: ordered array of `{path, line}` entries
- `program`: serialized root AST node, whose kind is `Program`

JSON is UTF-8. Object keys are serialized deterministically; non-finite numbers are forbidden. The serializer emits compact semantics, not comments or original whitespace.

## Node representation

Each node has exactly `kind`, `line`, and `fields`. `line` is a positive 1-based source line. Field sets are closed and defined by `compiler/ir.py` (`NODE_FIELDS`); unknown kinds, missing fields, and extra fields are invalid.

Supported v1 node kinds are: Program, Declare, Print, Input, If, While, For, Function, Return, Assign, IndexAssign, Variable, Literal, Try, Unary, Binary, List, Dict, Index, and Call. A feature absent from this list is not representable in IR v1 and must not be silently encoded as another node.

## Resource limits

The current validator enforces an 8 MiB input limit, maximum nesting depth 128, maximum 100,000 nodes, maximum 100,000 items per collection/object, and maximum 1,000,000 characters per string. Numbers must be finite. Implementations must reject malformed documents safely rather than partially executing them.

## Compatibility policy

1. **Patch:** clarification or validator bug fix that does not change valid v1 documents or their meaning.
2. **Minor language release:** new language features may be represented in v1 only if they fit the existing node schema without changing any existing node's meaning. Such changes still require fixture coverage and explicit review.
3. **Breaking IR change:** any change to required keys, node fields, value encoding, source-map semantics, or existing node meaning requires `ir_version: 2`, a migration note, and old-version fixtures.
4. Readers must reject unsupported future versions explicitly. Never reinterpret an unknown version as v1.
5. Deterministic serialization and source locations are part of the contract.
6. The IR is an interchange artifact, **not** a stable public API until a release is explicitly declared stable.

## Conformance gates

Before changing the format, add fixtures for:
- valid serialization round-trip and deterministic output;
- every node kind and field shape;
- unknown version/kind, missing and extra fields;
- invalid source locations, non-finite numbers, and resource limits;
- unsupported language feature diagnostics.

## Current implementation boundary

IR production and validation currently run in Python and depend on the Python parser/AST. This specification does not claim that IR generation is self-hosted or Python-free.
