# PusingCuk — Current Status and Priorities

**Branch originally targeted by this work:** `warungpusingcuk`  
**Language contract:** `0.6-dev`  
**Python package:** `0.8.0.dev0`  
**Status:** experimental. This summary does not prove that every test or deployment target passes, and it does not claim that the language is stable or that AI is generally accurate.

**AI knowledge/retrieval baseline:** 26 curated source documents; 22 baseline cases returned a top-1 result. The retrieval report is separate evidence and does not prove that a model was trained from scratch.  
**Historical retrieval baseline:** 5/8 (62.5%) and 6/8 (75%) in recorded evaluations. These remain historical results, not claims of general quality.

## Current state

**Conformance snapshot recorded in this document:** 78 fixtures: 78 required on the Python reference interpreter, 75 required on native C, and 3 explicitly unsupported on native C. The warung cashier example is included as a required test on both runtimes. Re-check the current fixture manifest and CI before relying on these historical counts.

- **Language:** lexer, parser, AST, reference interpreter, specification, built-in contract, and fixtures are present. The reference path still requires Python.
- **Native C:** a standalone backend/runtime exists for a subset. Features not covered by native tests must not be claimed compatible.
- **Bytecode/VM:** an experimental bytecode compiler and VM exist. This is not equivalent to a Python-free native runtime.
- **JavaScript/Python/Android:** backends or prototypes exist with their own coverage. File presence does not prove parity or distribution readiness.
- **PusingCuk AI:** assistant code and compiler tools exist. The assistant can help generate or repair .cuk, but is not a self-trained foundation model and must not claim code works merely because it generated it.
- **Frontend/backend SaaS:** existing UIs, services, and integrations remain prototypes until build, authentication, API, and runtime paths are verified on the same commit.

## Priority order

### P0 — Documentation and a single contract

1. Keep the README concise and `docs/README.md` as the documentation index.
2. Use `SPEC.md` for user-visible language behavior, `docs/SEMANTIC_CONTRACT.md` for semantics, and `library/builtin_contract.json` for built-in metadata and target support.
3. Treat dated audits as historical evidence, not current status. Avoid contradictory copies of roadmaps.
4. Every support claim must point to an implementation and target-specific test/fixture.

### P1 — Reduce Python dependence measurably

1. Make AST/IR behavior independent of accidental Python behavior.
2. Expand native C based on reproducible gaps, one behavior at a time; do not merely increase the number of built-in names.
3. For each gap: positive/negative fixture → specification → target implementation → conformance test.
4. Complete priority collections, functions, diagnostics, and built-ins across reference/native paths before claiming parity.
5. Measure binary size, startup time, memory, and runtime requirements before claiming the result is lightweight.
6. Separate **compiling on a developer machine** from **running the compiled artifact**. A standalone target is proven Python-free only when it runs without Python installed.

### P2 — PusingCuk AI → .cuk → evidence loop

1. Reuse the existing PusingCuk engine/tools; do not create an unnecessary second AI path.
2. AI proposes a .cuk program and explains the changes.
3. The compiler returns structured diagnostics.
4. Conformance tooling runs registered fixtures and returns evidence per runtime.
5. AI repairs from real diagnostics; results remain unverified until required runtimes pass.
6. Add fixtures only for reproducible semantic gaps.

### P3 — Separate application responsibilities

- **Frontend:** presentation, navigation, input, and UI validation.
- **Backend:** authentication, APIs, access policy, and service operations.
- **.cuk runtime:** deterministic rules and language behavior.
- **Library:** shared functions and adapters with explicit contracts.
- **Platform bridge:** device/storage capabilities requiring explicit permission.

Do not move business rules into the UI just to make a prototype look complete.

## Evidence required before calling work complete

- Language changes: relevant tests and reference/native fixtures.
- Compiler backend: backend tests and fixtures for the supported subset.
- AI: tool tests and compile/diagnostic/runtime flow; a model response is not proof.
- Web/SaaS: build, API, authentication, and main user flow actually executed.
- Android/desktop: artifact built and tested on the real target; an old APK or workflow file is not enough.

## Security boundaries

The runtime is not an OS sandbox that guarantees untrusted code is safe. Do not run unknown user code with access to private resources. Never put API keys, Supabase service-role keys, or credentials in source code, docs, logs, or prompts.

## Canonical sources

- [Vision](VISION.md)
- [Language specification](../SPEC.md)
- [Semantic contract](SEMANTIC_CONTRACT.md)
- [Target compatibility](COMPATIBILITY.md)
- [Built-in contract](../library/builtin_contract.json)
- [Documentation index](README.md)

Dated audits and old integration notes remain historical context until their claims are checked against current implementation. Do not assume every old recommendation is still an active priority.
