# Bytecode VM PusingCuk

PusingCuk now has a versioned stack-bytecode format and a reference VM. The bytecode is a separate executable format, unlike AST-preserving JSON IR.

## Compile and run

```sh
python -m compiler program.pusingcuk --target vm -o program.pbc.json
python -m compiler.vm program.pbc.json
```

The compiler parses and validates the source before emitting bytecode. The VM validates the bytecode envelope and instructions before execution. It has an instruction budget and a function-call depth limit; it is **not a security sandbox** for untrusted programs.

## Implemented instructions

Constants, variables, input/output, arithmetic/comparison/logical operations, short-circuit jumps, list and dictionary creation, indexing/mutation, conditionals, while/for loops, built-in `panjang` and `rentang`, functions and return values.

## Interoperability architecture

- `json`: AST-preserving IR v1 for tools and editors.
- `vm`: executable PusingCuk bytecode for the reference VM.
- `js`, `python`, `html`: source and browser targets.

Bytecode v1 is designed as a portable compiler artifact. It is not WebAssembly and is not yet a stable external ABI. Future work can add a verifier, binary encoding, debugger/source maps, optimization passes, and a WASM backend without confusing interchange JSON with executable bytecode.
