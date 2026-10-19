# PusingCuk

> **Warung language. Serious engineering.**

PusingCuk is an experimental programming language with the canonical `.cuk` extension, Indonesian-inspired keywords, and a distinct vocabulary shaped by Gen Z and Gen Alpha culture. Its identity is playful; its implementation contracts and evidence standards are deliberately strict.

[Open the experimental browser playground](https://rllibo833-sudo.github.io/pusingcuk/playground.html). The current playground uses Python through Pyodide as a temporary execution path; it is not the native `.cuk` runtime.

<!-- BEGIN GENERATED PYTHON-FREE SCORE BADGE -->
[![Python-free runtime · native C · 74/77 fixtures](docs/assets/python-free-score.svg)](docs/COMPATIBILITY.md)
Python-free native C score: **74 of 77 fixtures (96.10%)** in the checked-in compatibility snapshot. This score describes the native C source runtime and its required fixture subset; it does not measure the C bytecode VM or prove that the whole toolchain is Python-free.
<!-- END GENERATED PYTHON-FREE SCORE BADGE -->

**Development status:** language contract `0.6-dev`; Python package `0.8.0.dev0`. Python package version on main: `0.8.0.dev0`. This is experimental software, not a stable release. Support differs by runtime and backend; consult the compatibility evidence for the exact tested scope.

## What exists today

| Component | Verified scope | Important limitation |
|---|---|---|
| Language frontend | Lexer, parser, AST, reference interpreter, language specification, semantic contract, built-in contract, and conformance fixtures | The reference path requires Python |
| Native C runtime | Executes the subset represented by the native C conformance results | It is not feature-equivalent to the reference interpreter |
| Python bytecode VM | Experimental bytecode compiler and VM | Not a Python-independent deployment runtime |
| Native C bytecode VM | Loads versioned bytecode and runs a tested subset; six valid parity examples and four invalid-input checks are exercised by a dedicated test | This small test set is not full-language parity; the Python bytecode compiler remains in the test path |
| Other compiler targets | Experimental JavaScript, Python-transpiler, IR, and Android-related components | File presence does not establish full compatibility or release readiness |
| PusingCuk AI | Local-first assistant, provider adapters, curated retrieval, citations, local memory, and compiler-check tools | Uses selected model providers; it is not a foundation model trained by this project |
| AI repair loop | Provider-neutral core with compiler, fixture, and differential-result gates plus JSONL attempt logging | The production model adapter and canonical fixture/matrix callbacks are not yet wired into one end-to-end flow |

## Start here

- **New to the language:** [Getting started](docs/PEMULA.md)
- **Language behavior:** [Language specification](SPEC.md) → [Semantic contract](docs/SEMANTIC_CONTRACT.md)
- **Measured runtime support:** [Compatibility evidence](docs/COMPATIBILITY.md) and [conformance fixtures](docs/CONFORMANCE_FIXTURES.md)
- **Language vocabulary:** [English dictionary](docs/DICTIONARY.md) and [Gen Z/Gen Alpha vocabulary](docs/KOSAKATA_GENZ.md)
- **Project direction and current status:** [Project status](docs/PROJECT_STATUS_AND_ROADMAP.md) · [Documentation index](docs/README.md)
- **AI architecture:** [AI readiness](docs/AI_ENGINE_READINESS.md) · [Phase 6 repair loop](docs/PHASE6_PUSINGCUK_AI_REPAIR_LOOP.md)
- **Contribution and security:** [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md)

## Evidence rules

- **Implemented** means code exists.
- **Tested** means a named test ran against a named target at a specific commit.
- **Compatible** means the relevant shared fixtures passed on the compared targets.
- **Python-free** applies only to the exact execution path demonstrated to work without Python; it does not automatically apply to the build, compiler, or other runtime.
- **Production-ready** requires additional security, packaging, operations, and target-environment evidence.

A passing CI run proves only the checks actually executed by that workflow. It does not prove that every backend is equivalent, that arbitrary code is safe, or that the AI's output is correct.

## Security boundary

The interpreter, compiler, and VM are **not operating-system sandboxes**. Do not run untrusted source or bytecode in a sensitive environment. VM instruction, time, and memory budgets are runtime guardrails, not hard OS-level isolation.

## License

PusingCuk is distributed under the MIT License. See [LICENSE](LICENSE).
