# PusingCuk — Project Overview

> **Warung-language feel. Serious machinery.**

**Documentation snapshot:** 18 October 2026  
**Language contract:** `0.6-dev`  
**Python package:** `0.8.0.dev0`  
**Maturity:** experimental / alpha — not a stable release.

This document summarizes the repository for readers, contributors, and potential users. Implementation status can change; use the compatibility matrix and fixtures from the commit you are evaluating for technical decisions.

## What is PusingCuk?

PusingCuk is an experimental programming language with the primary `.cuk` extension, Indonesian keywords, and vocabulary inspired by conversational language. It aims to make syntax feel familiar while serving as an open laboratory for interpreters, compilers, runtimes, and developer tools.

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

| Component | Purpose | Important limitation |
|---|---|---|
| `lexer.py`, `parser.py`, `ast_nodes.py` | Convert source text into tokens and program structure | Must remain aligned with SPEC and fixtures |
| `evaluator.py`, `pusingcuk_new.py` | Python reference interpreter | The reference path requires Python |
| `compiler/` | IR and experimental backends | Each target supports a different subset |
| `native/` | C runtime for a tested subset | Not fully equivalent to the reference interpreter |
| `library/` | Built-in contracts, machine vocabulary, functions, and adapters | Registry entries do not imply every target supports every feature |
| `tests/`, `tools/conformance.py` | Unit tests and conformance evidence | Results apply only to the tests and commit that ran |
| `examples/` | Learning and trial programs | Examples do not prove production readiness |
| AI assistant modules | Tools to support the .cuk workflow | Do not prove a self-trained foundation model or universally correct output |
| `web/`, `site/`, `android-studio/` | Existing UI, website, and distribution prototypes | Source files do not prove a production service or app |
| `.github/workflows/` | Automated tests, builds, and packaging | Workflows may have different triggers and scopes; inspect the latest run |

## Reasonable use cases

- Learn program structure, variables, conditions, loops, functions, collections, and documented built-ins.
- Explore language design through the specification and fixtures.
- Generate experimental target artifacts for supported subsets.
- Run a supported subset through the C runtime after the required build.
- Use available examples and AI tools to accelerate .cuk experiments, while validating results with compiler/runtime evidence.

## How to interpret feature claims

Use these levels consistently:

1. **Present in the repository** — a file or implementation exists.
2. **Works on a specific path** — a matching example or check has run.
3. **Verified** — relevant target fixtures passed on the same commit.
4. **Production-ready** — requires further evidence for security, reliability, deployment, monitoring, and real target environments.

Do not conflate these levels. Compiler targets, Android examples, web interfaces, adapters, and AI modules must each be assessed according to their execution path.

## Current gaps and risks

- **Not stable:** contract version `0.6-dev` and package version `0.8.0.dev0` indicate ongoing development, not a stable API.
- **Limited parity:** the reference interpreter, C runtime, JavaScript, Python, HTML, and VM do not automatically have identical coverage.
- **Reference path requires Python:** the standalone C runtime supports only the subset explicitly listed and tested.
- **Incomplete ecosystem:** cross-runtime modules, stable ABI/FFI, WebAssembly, complete browser bindings, and production database/blockchain integration must not be marketed as finished capabilities.
- **Security boundary:** code execution is not an OS sandbox; untrusted code can pose risks to process resources.
- **AI is not an oracle:** generated output must be checked by the compiler, tests, and runtime. An assistant module is not the same as a self-trained foundation model.
- **Distribution readiness varies:** a successful build does not prove installation and use work on every target device.
- **Historical documentation:** dated audits and roadmaps must be distinguished from active status and must not be used as sole evidence.

## Recommended priorities

1. Keep `SPEC.md`, the semantic contract, built-in contract, fixtures, and compatibility matrix aligned as one evidence chain.
2. Fix reproducible CI failures before adding features.
3. Expand runtime support based on semantic gaps and specific tests, not feature-name counts.
4. Keep the dictionary and beginner guide approachable; put implementation details in technical docs.
5. Label AI, UI, packaging, and compiler-target features according to current evidence.
6. Review workflow security and test distribution on real target environments before making production claims.

## Outside the product promise

This document does not promise a stable language, full parity across all targets, a self-trained AI model, a general security sandbox, a ready-to-use SaaS service, or production support for integrations that remain on the roadmap.

## Canonical references

- [Language specification](../SPEC.md)
- [Semantic contract](SEMANTIC_CONTRACT.md)
- [Compatibility](COMPATIBILITY.md)
- [Built-in contract](../library/builtin_contract.json)
- [Conformance fixtures](CONFORMANCE_FIXTURES.md)
- [Warung-language dictionary](KAMUS_PUSINGCUK.md)
