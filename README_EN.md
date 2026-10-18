# PusingCuk

PusingCuk is an experimental programming language with the `.cuk` extension, Indonesian-language keywords, and its own syntax identity. The project focuses on the language, interpreter, compiler, runtime, and runnable examples that contributors can improve.

**Status:** language contract `0.6-dev`; Python package `0.8.0.dev0`. This is development software, not a stable release. Backend support differs; do not assume every program behaves identically across targets.

## Try .cuk

Requirements: Python 3.11 or 3.12.

```sh
python pusingcuk_new.py halo.cuk
```

Example `halo.cuk`:

```cuk
jancuk
lah nama = "Dunia"
hedeh "Halo, " + nama
selesai jancuk
```

Check syntax without executing:

```sh
python pusingcuk_new.py --check halo.cuk
```

## Project map

- `lexer.py`, `parser.py`, `evaluator.py`: reference language path.
- `compiler/`: IR and compiler backends with explicitly limited support.
- `native/`: C runtime for the declared language subset.
- `library/`: built-ins and language contracts.
- `examples/`: runnable examples.
- `tests/conformance/`: fixtures that lock language behavior.

Start with [the language specification](SPEC.md), [semantic contract](docs/SEMANTIC_CONTRACT.md), and [contributing guide](CONTRIBUTING.md).

## Security limits

The interpreter and backends are not an operating-system sandbox. Do not run untrusted .cuk code or bytecode in sensitive environments. An experimental VM does not automatically provide security isolation.

## License

MIT. Contributions to the language, runtime, compiler, examples, and compatibility are welcome.
