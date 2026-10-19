# Phase 4 — Path Away from Python

**Goal:** make Python optional for end users incrementally, with every step gated by reproducible fixtures. This roadmap records partial implementation; it does not claim that the final goal has been reached.

## Gate 1 — Versioned formats

- [x] Document JSON IR v1 envelope, nodes, limits, and compatibility policy.
- [x] Document bytecode v1 envelope, opcodes, and compatibility policy.
- [ ] Add executable schema/version fixtures and require them in CI before declaring either format release-stable.

## Gate 2 — Native C bytecode VM

**Status: a tested subset exists; full gate remains open.**

The repository now contains a native C bytecode executable that reads serialized bytecode and executes a limited opcode subset without invoking Python in the C VM process. CI builds the executable and compares six deterministic programs against the Python VM. Four malformed or invalid bytecode cases are expected to be rejected.

This is meaningful progress, but it is not full-language conformance. The Python bytecode compiler is still used to produce the input in the parity test, and the current six examples do not cover every required manifest fixture. The native C source runtime's 74/77 score is a separate measurement and must not be reused as a C bytecode VM score.

Acceptance criteria:

- [x] Native C VM loads serialized bytecode without invoking Python inside the VM process.
- [x] Invalid JSON, unknown opcode, invalid jump, and step-limit cases are checked by the dedicated test.
- [ ] Expand parity coverage by reusing eligible canonical manifest fixtures rather than maintaining a disconnected sample set.
- [ ] Compare exit code, stdout, diagnostic class, and source line for all fixtures required on the C VM target.
- [ ] Publish a separate C bytecode VM result; do not increase the native C source-runtime score from VM-only results.

## Gate 3 — Self-host the lexer

**Status: not implemented.**

- Define the smallest .cuk subset capable of implementing the lexer.
- Implement the lexer in .cuk and compare token kind, lexeme, line, column, and diagnostics against the Python lexer using golden fixtures.
- If required language primitives are missing, add a focused fixture and implement the primitive before expanding the self-hosted lexer.
- Do not use hidden Python helpers to simulate self-hosting.

## Gate 4 — Self-host the parser

**Status: not started; blocked on Gate 3.**

Implement the parser in .cuk only after the lexer gate passes. Compare normalized AST/IR and parse diagnostics against the reference parser using the same corpus.

## Gate 5 — Compiler on the VM

**Status: long-term goal.**

The compiler should eventually be written in .cuk and execute on a sufficiently capable bytecode VM. Python may remain a bootstrap/development tool, but must not be required at runtime for a path advertised as Python-free.

## Release criteria

- Each gate has named fixtures, expected outputs/diagnostics, and a CI job.
- Unsupported constructs and targets are recorded explicitly rather than silently bypassed.
- Compatibility reports identify the exact target, command, fixture corpus, and commit.
- No Python-free claim is made for a path that invokes Python during the claimed execution.
