# PusingCuk Bytecode Specification

**Status:** Frozen format v1 for the 0.6-dev language line.  
**Format identifier:** `pusingcuk-bytecode`  
**Version field:** `bytecode_version: 1`

The canonical producer and validator are in `compiler/bytecode.py`; the reference VM is `compiler/vm.py`. This document describes the persisted envelope and instruction representation. The Python VM is not a native C bytecode VM.

## Envelope

The bytecode document contains:
- `format`: `pusingcuk-bytecode`
- `bytecode_version`: integer `1`
- `language_version`: language version string
- `source_name`: source basename or memory label
- `functions`: map from function name to `{params, code}`
- `code`: main instruction array

Each instruction is a three-element array: `[opcode, operand, source_line]`. The source line is a positive 1-based integer. Opcode names are case-sensitive. The opcode set is enforced by `compiler.bytecode.OPS`.

## Opcode set v1

`CONST`, `LOAD`, `DECLARE`, `STORE`, `PRINT`, `INPUT`, `POP`, `MAKE_LIST`, `MAKE_DICT`, `GET`, `SET_INDEX`, `UNARY`, `BINARY`, `TO_BOOL`, `JUMP`, `JUMP_IF_FALSE`, `JUMP_IF_TRUE`, `CALL`, `ITER_INIT`, `ITER_NEXT`, `RETURN`.

Operands are opcode-specific and validated by `validate_bytecode()`. Jump targets must be within the valid instruction boundary. Function entries contain parameter names and their own instruction arrays. Execution limits and diagnostic behavior belong to the VM contract, not the serialized encoding.

## Compatibility policy

1. A v1 patch must preserve the meaning and operand shape of every existing opcode.
2. Do not repurpose an opcode or silently change operand interpretation.
3. A new opcode may be added to v1 only when old readers can reject it safely and the compatibility policy explicitly accepts forward incompatibility; otherwise introduce bytecode v2.
4. Any change to the envelope, instruction tuple shape, existing opcode semantics, or control-flow operand encoding requires a new `bytecode_version`, migration notes, and v1/v2 fixtures.
5. Readers must reject unsupported future versions and unknown opcodes with a controlled diagnostic.
6. Bytecode is untrusted input. Validate the entire document and control-flow operands before execution; enforce step and call-depth limits.
7. A format version does not imply stable language semantics or a native implementation.

## Conformance gates

Required fixtures cover:
- deterministic compile output and JSON round-trip;
- each opcode and each operand shape;
- invalid envelope/version/opcode/instruction length/source line;
- invalid jump targets, stack underflow, invalid collection counts, and call arity;
- execution output and diagnostics across reference VM and every claimed target.

## Current implementation boundary

The Python compiler emits v1 bytecode and the Python VM executes it. The current native C runtime executes source through its own implementation; a C VM that consumes this bytecode has **not** been established by this branch. Therefore the current Python-Free Score must not count Python bytecode VM execution as Python-free.
