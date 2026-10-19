# PusingCuk — Project Overview

> **Warung-language feel. Serious machinery.**

**Documentation snapshot:** 19 October 2026  
**Language contract:** `0.6-dev`  
**Python package:** `0.8.0.dev0`  
**Maturity:** experimental / alpha; not a stable release.

This page summarizes the repository for readers, contributors, and potential users. For current claims, check the compatibility snapshot and CI evidence for the exact commit in use.

## What is PusingCuk?

PusingCuk is an experimental programming language with the canonical `.cuk` extension, Indonesian-inspired keywords, and a vocabulary rooted in conversational language. The project explores an approachable learning experience while building real interpreter, compiler, runtime, and developer-tool infrastructure.

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
| `lexer.py`, `parser.py`, `ast_nodes.py` | Tokenization, parsing, and syntax-tree construction | Must remain aligned with the language specification and fixtures |
| `evaluator.py`, `pusingcuk_new.py` | Python reference interpreter | The reference execution path requires Python |
| `compiler/` | IR, bytecode, and experimental compiler backends | Each target supports a different subset |
| `native/` | Native C runtime and C bytecode VM | They are separate execution paths and must be measured separately |
| `library/` | Built-in contracts, vocabulary metadata, assistant, provider adapters, and tools | Registry entries do not prove support in every runtime |
| `tests/`, `tools/conformance.py` | Unit tests and reproducible behavior checks | Results apply only to the targets and commit actually tested |
| `examples/` | Learning examples and compatibility programs | An example is not proof of full target compatibility |

## Current measured baseline

The checked-in compatibility snapshot reports 77 fixtures: 77 pass on the reference interpreter, while native C passes 74 and explicitly marks 3 unsupported. The reported 96.10% score applies only to the native C source runtime against that fixture set.

The native C bytecode VM has a separate targeted test with six valid Python/C output-parity examples and four invalid-input rejection cases. This does not yet prove full-language VM parity.

PusingCuk AI has a local-first assistant, model-provider adapters, curated retrieval, citations, local memory, and compiler-check tools. It is an assistant layer over a selected provider model, not a foundation model trained by this project. The Phase 6 repair-loop core is implemented, but production provider, persistent fixture, and full-matrix callbacks are still pending integration.

## Recommended reading

- [Project vision](VISION.md)
- [Language specification](../SPEC.md)
- [Semantic contract](SEMANTIC_CONTRACT.md)
- [Compatibility evidence](COMPATIBILITY.md)
- [Conformance fixtures](CONFORMANCE_FIXTURES.md)
- [AI readiness](AI_ENGINE_READINESS.md)
- [Current project status](PROJECT_STATUS_AND_ROADMAP.md)

## Security boundary

The interpreter, compiler, and VM are not operating-system sandboxes. Capability strings do not mediate host operations unless the operations explicitly invoke the policy. Resource budgets are runtime guardrails, not hard OS-level isolation.
