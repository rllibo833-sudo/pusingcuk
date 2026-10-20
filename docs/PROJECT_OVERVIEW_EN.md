# PusingCuk — Project Overview

> **Warung-language feel. Serious machinery.**

**Documentation snapshot:** 20 October 2026 (main implementation review)  
**Language contract:** `0.6-dev`  
**Python package:** `0.8.0.dev0`  
**Maturity:** experimental / alpha — not a stable release.

This document summarizes the repository for readers, contributors, and prospective users. Implementation status can change; use the compatibility matrix and fixtures from the exact commit you intend to use.

## What is PusingCuk?

PusingCuk is an experimental programming language using the `.cuk` extension, Indonesian keywords, and a distinctive conversational vocabulary. Its goal is to make syntax feel approachable while providing an open laboratory for interpreter, compiler, runtime, and developer-tool experiments.

Example:

```cuk
jancuk
lah nama = "Dunia"
fungsi sapa(orang)
    balek "Halo, " + orang
selesai fungsi
hedeh sapa(nama)
selesai jancuk
```

## Repository map

| Component | Purpose | Important limit |
|---|---|---|
| `lexer.py`, `parser.py`, `ast_nodes.py` | Turn source text into tokens and program structure | Must remain aligned with SPEC and fixtures |
| `evaluator.py`, `pusingcuk_new.py` | Reference Python interpreter path | The reference path requires Python |
| `compiler/` | IR and experimental backends | Each target supports a different subset |
| `native/` | C runtime for a tested subset | Not fully equivalent to the reference interpreter |
| `library/` | Built-in contract, machine-readable vocabulary, functions, and adapters | Registry presence does not imply universal target support |
| `tests/`, `tools/conformance.py` | Unit tests and conformance evidence | Results apply only to checks and commits that actually ran |
| `tools/reality_engine.py`, `tools/diagnostic_repair_loop.py`, `tools/local_ai_adapter.py` | Fail-closed proposal gate, syntax diagnostics, and separate legacy AI repair adapter | Default gate cannot accept a new proposal; diagnostic helper does not execute code |
| `src/backends/`, `src/c-core/` | Draft PVM v1 transpilers and assembler | Separate from `compiler/vm.py`; PVM v1 is experimental and not a sandbox |
| `examples/` | Learning and smoke-test programs | Examples do not prove production readiness |
| `library/assistant.py` and related modules | PusingCuk AI tools for the .cuk development loop | Does not prove a self-trained foundation model or universally correct output |
| `web/`, `site/`, `android-studio/` | Existing UI, site, and distribution prototypes | Code presence is not equivalent to a production service/app |
| `.github/workflows/` | Test, build, and packaging automation | Workflows can have different triggers and coverage; inspect recent results |

## Reasonable use cases

- Learn program structure, variables, conditions, loops, functions, collections, and documented built-ins.
- Explore language design using specifications and fixtures.
- Generate experimental target artifacts for supported subsets.
- Run the supported subset through the C runtime after building it appropriately.
- Use available examples and AI tools to assist .cuk experiments, while treating compiler/runtime checks as the evidence.

## How to interpret feature claims

Use these four levels consistently:

1. **Present in the repository** — a file or implementation exists.
2. **Works on a specific path** — an example or relevant result exists.
3. **Verified** — the relevant target tests/fixtures passed on the same commit.
4. **Production-ready** — requires additional evidence for security, resilience, deployment, monitoring, and real target environments.

These levels are not interchangeable. Compiler targets, Android examples, web interfaces, adapters, and AI modules must be evaluated on their own execution paths.

## Current limitations and risks

- **Not stable:** language contract `0.6-dev` and package `0.8.0.dev0` indicate development software, not a stable API guarantee.
- **Limited parity:** the reference interpreter, C runtime, JavaScript, Python, HTML, and VM do not automatically share identical feature coverage.
- **Python-dependent reference path:** the standalone C runtime covers only the declared and tested subset.
- **Incomplete ecosystem:** cross-runtime modules, stable ABI/FFI, WebAssembly, complete browser bindings, and production database/blockchain integrations must not be advertised as finished.
- **Security boundary:** execution is not an OS sandbox; untrusted code may pose risks to process-accessible resources.
- **AI is not an oracle:** generated output must be checked by the compiler, tests, and runtime. An assistant module is not the same as a self-trained foundation model.
- **Distribution readiness varies:** a successful build does not prove installation and operation on every target device.
- **Historical documentation:** dated audits and roadmaps must be distinguished from current status and are not sufficient evidence by themselves.

## Recommended priorities

1. Keep SPEC, the semantic contract, built-in contract, fixtures, and compatibility matrix in one evidence chain.
2. Fix reproducible CI failures before adding features.
3. Expand runtime support based on specific semantic gaps and tests, not feature counts.
4. Keep the dictionary and beginner guide as learning paths, with implementation details in technical docs.
5. Label AI, UI, packaging, and compiler targets according to current evidence.
6. Run workflow security checks and target-environment distribution tests before making production claims.

## What this overview does not promise

This document does not promise a stable language, full cross-target compatibility, a self-trained AI model, a general-purpose security sandbox, a ready-to-use SaaS, or production support for integrations that remain roadmap items.

## Canonical references

- [Language specification](../SPEC.md)
- [Semantic contract](SEMANTIC_CONTRACT.md)
- [Compatibility matrix](COMPATIBILITY.md)
- [Built-in contract](../library/builtin_contract.json)
- [Conformance fixtures](CONFORMANCE_FIXTURES.md)
- [Kamus Bahasa Warung](KAMUS_PUSINGCUK.md)
