# PusingCuk — Current Status and Priorities

**Snapshot:** 20 October 2026 · branch `main` at `cc7c8f47f0f8` (before this documentation synchronization).
**Language contract:** `0.6-dev`  
**Python package:** `0.8.0.dev0`  
**Status:** experimental. This summary does not prove that every test or deployment target passes, and it does not claim that the language is stable or that AI is generally accurate.

**AI knowledge/retrieval baseline:** 26 curated source documents; 22 baseline cases returned a top-1 result. The retrieval report is separate evidence and does not prove that a model was trained from scratch.  
**Historical retrieval baseline:** 5/8 (62.5%) and 6/8 (75%) in recorded evaluations. These remain historical results, not claims of general quality.

## Current state

**Verified conformance snapshot:** 77 active fixtures. On commit `cc7c8f47f0f800faa24ec93584adceecc32778d2`, the fixture matrix passed 77/77 on the reference interpreter and 74/77 on native C, with 3 native fixtures explicitly unsupported. The same run measured JavaScript 29/77, Python transpiler 21/77, VM 28/77, and HTML 0/77 executable fixtures. The reference/native differential report compared 74 cases with 0 mismatches, 0 incomplete comparisons, and 3 unsupported cases. These results describe only the measured fixtures, not full backend parity.

- **Language:** lexer, parser, AST, reference interpreter, specification, built-in contract, and fixtures are present. The reference path still requires Python.
- **Native C:** a standalone backend/runtime exists for a subset. Features not covered by native tests must not be claimed compatible.
- **Bytecode/VM:** an experimental bytecode compiler and VM exist. This is not equivalent to a Python-free native runtime.
- **JavaScript/Python/Android:** backends or prototypes exist with their own coverage. File presence does not prove parity or distribution readiness.
- **PusingCuk AI:** the assistant, retrieval, provider adapters, allowlisted tools, compile-check, and file-generation tool exist. The separate repair adapter is not yet an end-to-end accepted repair pipeline: the default Reality Engine runner has no integrated JS/Python/VM proposal runners or fixture-addition evidence.
- **Cuk Reality Engine:** a fail-closed acceptance gate exists, but the production runner currently marks JavaScript, Python, and VM unavailable and requires a relevant fixture to already be added. It is a gate/prototype, not proof of autonomous cross-target repair.
- **Installed AI tooling:** source inspection shows the AI tools resolve `tests/conformance/manifest.json`, but neither the setuptools package data nor the PyInstaller data list includes `tests/conformance/`. This is an unverified packaging gap to close before relying on conformance/context tools from installed distributions.
- **Adapters:** SQLite, loopback HTTP, and mock/loopback JSON-RPC host modules exist, but the language-level capability contract still marks database, server HTTP, DOM, Web3, and stable FFI as planned because they are not first-class `.cuk` APIs or claimed compiler targets.
- **Frontend/backend SaaS:** existing UIs, services, and integrations remain prototypes until build, authentication, API, and runtime paths are verified on the same commit.

## Branch audit (20 October 2026)

The following branches are divergent from `main`; branch-only work is not part of the main implementation unless separately integrated and verified.

| Branch | Code-only findings | Current disposition |
|---|---|---|
| `compatibility-generator` | Older revision of `tools/generate_compatibility.py` and workflow changes | `main` already has a more complete generator; do not merge the branch wholesale |
| `core-cuk-engine` | `compiler/sandbox.py`, `native/bytecode_vm.c`, additional reports/tests/workflow | Review individual components before porting; no claim that they run on `main` |
| `cuk-reality-engine` | `compiler/repair_loop.py`, `compiler/offline_repair.py`, `compiler/sandbox.py`, native bytecode VM and Reality Engine workflow | Potential repair/sandbox work is branch-only and not wired into current main AI tools |
| `public-site` | Different `site/` content, logo, sitemap/robots, and Pages workflow | Selectively compare the site changes; the branch is not a current mirror of `main` |

Do not merge these branches as a single bundle: each is behind/diverged, and current `main` has since changed contracts, tests, and implementation paths.
## CI and packaging boundaries

- The `package.yml` push trigger still targets `warungpusingcuk`, which is not in the current branch list. Manual `workflow_dispatch` remains available. Do not retarget this Android/package-heavy workflow to every `main` push without an explicit decision about runner cost.
- `fixture-baseline.yml` still references `actions/checkout@v4`, `actions/setup-python@v5`, and `actions/upload-artifact@v4` by mutable major tags, while most other workflows pin action commit SHAs. This is a supply-chain hardening gap, not evidence of compromise.
- The 13 checked-in workflows contain no `pull_request_target` or `workflow_run` trigger. The release workflow separates its read-only build job from a publish job with `contents: write`; the latter runs only after the validated release-artifact job.
- Packaging and installed-AI gaps are separate: the Python wheel/PyInstaller build omits `tests/conformance/manifest.json`, although AI tools look it up under `tests/`. A green source-tree test suite does not prove those installed AI tools can load fixture context.

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
