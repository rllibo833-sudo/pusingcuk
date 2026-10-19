# Phase 4 — Path Away from Python

Goal: make Python optional for end users incrementally, with every step gated by reproducible fixtures. This is a roadmap, not a claim that the end state already exists.

## Gate 1 — Freeze formats (documented in this branch)

- [x] Specify JSON IR v1 envelope, nodes, limits, and compatibility policy.
- [x] Specify bytecode v1 envelope, opcodes, and compatibility policy.
- [ ] Add executable version/schema fixtures and ensure CI runs them before declaring the formats release-stable.

## Gate 2 — Native C bytecode VM (not complete)

The current Python VM executes bytecode. The current native C target is not demonstrated to load and execute the bytecode format. Implement a C bytecode reader/validator/stack VM, starting with CONST, variable operations, arithmetic, output, and branches. Expand only when fixtures prove parity.

Acceptance criteria:
- C VM loads a serialized bytecode file without invoking Python.
- Invalid versions/opcodes/jumps fail safely.
- Reference VM and C VM agree on exit code, stdout, diagnostic class and source line for every fixture marked required on both targets.
- Python-Free Score is recomputed from actual C-VM executions. Do not award a pass merely because native source execution passes.

## Gate 3 — Self-host the lexer first (not complete)

- Define a narrow .cuk subset sufficient to implement the lexer.
- Write lexer implementation in .cuk; Python may compile/run the bootstrap during the initial stage.
- Compare token kind, lexeme, line, column and error diagnostics against the Python lexer using checked-in golden fixtures.
- If the language lacks strings/character handling, data structures, or other required features, file a roadmap issue and add a fixture. Do not use hidden Python helpers to fake self-hosting.

## Gate 4 — Self-host the parser (after lexer gate passes)

- Implement parser in .cuk using the accepted lexer output.
- Compare normalized AST/IR and parse diagnostics against the Python parser on the same corpus.
- Do not start until the lexer gate is green and the necessary language features are specified and tested.

## Gate 5 — Compiler on the VM (final goal)

The compiler should be written in .cuk and run on the bytecode VM. Python becomes an optional bootstrap/development tool, not a required runtime dependency for users. Release claims require a clean environment test with no Python executable on PATH.

## Release criteria

- Each gate has named fixtures, expected outputs/diagnostics, and a CI job.
- Unsupported features/targets are recorded as roadmap issues instead of bypasses.
- Compatibility reports include exact target identity and command.
- No “Python-free” claim is made for a path that invokes Python at runtime.
