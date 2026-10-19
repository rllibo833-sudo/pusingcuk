# Project Status and Engineering Priorities

**Status source:** this document is a maintained summary, not a substitute for commit-specific CI evidence. Verify the branch and commit linked below before reusing any measurement.

## Current evidence snapshot

- **Working branch for the Reality Engine and Phase 6 work:** `cuk-reality-engine`
- **Latest verified CI commit at the time of this update:** `c75c3637b02f0ff7d6dcf3a24bd900aa12e16017`
- **CI result:** successful — [workflow run 39190178886](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39190178886)
- **Language contract:** `0.6-dev`
- **Python package:** `0.8.0.dev0`
- **Checked-in compatibility snapshot:** 77 fixtures; reference interpreter 77 pass; native C source runtime 74 pass and 3 explicitly unsupported; reported native C score 74/77 (96.10%).
- **Separate C bytecode VM test:** six valid Python/C output-parity examples and four invalid-bytecode rejection cases. This is a small targeted test, not full-language VM conformance.
- **AI knowledge baseline:** the maintained AI readiness document reports 26 curated source records and 22 Indonesian retrieval regression cases. This is a small regression corpus, not a general accuracy score.

The compatibility snapshot measures the reference interpreter and native C source runtime. It must not be used as a score for the C bytecode VM, all compiler targets, or an entirely Python-free toolchain.

## Component status

| Component | Current implementation | Evidence required before a stronger claim |
|---|---|---|
| `.cuk` language | Lexer, parser, AST, reference interpreter, semantic specification, built-in metadata, and conformance fixtures | Shared fixtures for every claimed semantic behavior and target |
| Native C source runtime | A supported subset runs without Python after native compilation | Fixture parity for each supported feature; build-time Python requirements must be stated separately |
| Python bytecode VM | Experimental bytecode compiler and VM with resource-budget hooks | VM fixture coverage and explicit target-specific behavior |
| Native C bytecode VM | C executable reads serialized bytecode and executes a tested subset | Expand the dedicated parity suite; run the full eligible fixture matrix through the C VM before claiming broad compatibility |
| Compiler backends | JavaScript, Python transpiler, C code generation, IR, and Android-related prototypes exist with different scopes | Build and execution evidence per backend; do not infer support from filenames |
| PusingCuk AI | Local-first assistant, provider adapters, curated retrieval, citations, local memory, and allowlisted tools | End-to-end integration tests; a selected provider model is not a PusingCuk-trained foundation model |
| Phase 5 security | Default-deny capability policy and VM-level fuel/time/approximate-memory budgets | Host-operation mediation, negative integration tests, and external OS isolation for hostile code |
| Phase 6 repair loop | Provider-neutral proposal/validation core with attempt logs and fail-closed evidence gates | Real provider adapter, persisted fixture creation, canonical complete matrix execution, regression gate, and explicit accepted-source persistence |
| Web/SaaS and mobile | Prototypes and adapters may exist in the repository | Deployed build, authentication, API, end-to-end use, and target-device evidence |

## Branch and integration policy

This repository currently contains multiple long-lived engineering branches, including `main`, `core-cuk-engine`, `compatibility-generator`, `differential-runner`, and `cuk-reality-engine`. They are not interchangeable releases. The Reality Engine branch contains the latest Phase 5 and Phase 6 changes described above; earlier branches can lack later commits. Do not describe a feature as shared across branches until it has been integrated and verified there.

Do not merge branches merely to make their names disappear. For each useful change, check its ancestry and diff, integrate the implementation and its tests/fixtures together, then verify the resulting branch. Avoid duplicating an existing implementation or fixture in a second location.

## Engineering priorities

### P0 — One consistent evidence record

1. Keep this page and the README aligned with the same measured compatibility snapshot.
2. Generate counts from the manifest and report artifacts rather than hand-editing numbers.
3. Mark dated audits and old scores as historical; do not silently rewrite historical findings.
4. Every support claim must name its implementation, test/fixture, target, and limitation.

### P1 — Close the language/runtime gaps

1. Use the Python reference interpreter as an oracle while the native C and bytecode targets expand.
2. For each real semantic gap, add one focused fixture, implement the behavior, and run the relevant target matrix.
3. Include compiler diagnostics, source locations, exit codes, collection behavior, functions, and numeric boundaries in parity work.
4. Keep the built-in contract and user-facing library documentation synchronized when language-visible behavior changes.
5. Test a native artifact in an environment without Python before claiming that the execution path is Python-free.

### P2 — Make the C bytecode VM measurable

1. Keep the dedicated C VM parity test in CI.
2. Expand it by reusing eligible manifest fixtures rather than maintaining a duplicate, unrelated test catalogue.
3. Report the C VM separately from the native C source runtime.
4. Do not increase the Python-Free Score until the measured score explicitly covers the relevant execution path.

### P3 — Finish the AI-to-code evidence loop

1. Keep model output as an untrusted proposal.
2. Require a trusted expected behavior before accepting a new conformance fixture; never infer correctness from the model's own claim.
3. Persist the fixture, run the actual compiler and complete required matrix, and reject incomplete runs or regressions.
4. Log each attempt and persist proposed source only after all gates pass.
5. Keep provider choice separate from language semantics and never store credentials in source, prompts, fixtures, or logs.

### P4 — Avoid documentation-only progress

A change should deliver at least one of: user-visible behavior, a reproducible test/fixture, a real integration, or a correction to a demonstrably stale claim. Do not add another roadmap when an existing contract can be updated. Do not rerun the entire suite repeatedly when a relevant successful run already proves the unchanged commit; rerun after meaningful code or workflow changes.

## Security boundary

The interpreter, compiler, and VM are not operating-system sandboxes. Capability strings do not mediate host operations unless the operations explicitly call the policy. Memory accounting is approximate and time checks occur at VM instruction boundaries. Use external OS/container isolation for untrusted code.

## Canonical references

- [Language specification](../SPEC.md)
- [Semantic contract](SEMANTIC_CONTRACT.md)
- [Built-in contract](../library/builtin_contract.json)
- [Compatibility snapshot](COMPATIBILITY.md)
- [Conformance fixtures](CONFORMANCE_FIXTURES.md)
- [AI readiness](AI_ENGINE_READINESS.md)
- [Phase 5 capability policy](PHASE5_CAPABILITY_SANDBOX.md)
- [Phase 6 repair loop](PHASE6_PUSINGCUK_AI_REPAIR_LOOP.md)
