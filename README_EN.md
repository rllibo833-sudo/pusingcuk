# PusingCuk

PusingCuk is an experimental programming language with Indonesian-friendly keywords and the `.cuk` source extension. Its goal is approachable syntax backed by explicit semantics and testable runtime behavior.

- **Language contract:** `0.6-dev`
- **Python package:** `0.8.0.dev0`
- **Status:** experimental; target support is not uniform.

## Quick start

The current reference path requires Python 3.11 or newer:

```sh
python pusingcuk_new.py halo.cuk
```

## Repository map

- `.cuk` files: programs, examples, and deterministic rules.
- `lexer.py`, `parser.py`, `evaluator.py`: current Python reference path.
- `compiler/` and `native/`: experimental backends and native runtime.
- `library/`: built-in metadata, vocabulary, adapters, and examples.
- `web/`, `apps/`, `site/`, `supabase/`: UI/service prototypes and integrations.
- `tests/`: regression tests and conformance fixtures.
- `docs/README.md`: documentation index by responsibility.

## Python independence

The Python interpreter is still the reference implementation. A generated C executable can run without Python after compilation, but the C backend and native runtime support only documented subsets. JavaScript, Python-transpiler, bytecode VM, web, and Android support must be checked individually. A file or backend existing in the repository is not proof of release readiness.

The `cuk-reality-engine` branch includes a deterministic `.cuk` rules example, but it is not a standalone runtime or a self-hosting compiler. The example currently runs through the Python reference CLI. The rule-mapping functions now fail closed for unknown IDs, with a regression that injects an arbitrary ID. A JavaScript-target regression has been added for the same source and core input cases, but its result must be confirmed on the latest CI run; full native/JS/VM parity is not established because native C does not support the example's `coba/ketangkep` block. PusingCuk AI assists with `.cuk` code; it is not currently a foundation model trained from scratch. Model output is not proof of compilation or runtime correctness.

See [language specification](SPEC.md), [compatibility matrix](docs/COMPATIBILITY.md), [project status](docs/PROJECT_STATUS_AND_ROADMAP.md), and [main README](README.md).

PusingCuk is MIT-licensed. Runtime execution is not an OS sandbox: do not execute untrusted code.
