# Documentation Index

This index is the entry point for maintained PusingCuk documentation. Use implementation, tests, fixture manifests, and CI results from the same commit as the primary evidence. Historical audits and roadmap documents explain decisions; they are not automatically current status.

## 1. Project identity and language

- [Project vision](VISION.md)
- [Project overview](PROJECT_OVERVIEW_EN.md)
- [Language specification](../SPEC.md)
- [Semantic contract](SEMANTIC_CONTRACT.md)
- [Built-in contract](language/BUILTINS.md) and [machine-readable built-in metadata](../library/builtin_contract.json)
- [English dictionary](DICTIONARY.md)
- [Gen Z and Gen Alpha vocabulary](KOSAKATA_GENZ.md) and [language style](GAYA_BAHASA.md)

## 2. Compiler and runtime

- [Compatibility evidence](COMPATIBILITY.md) — generated snapshot for the reference interpreter and native C source runtime
- [Conformance fixtures](CONFORMANCE_FIXTURES.md) — fixture definitions and expected behavior
- [Compiler targets](COMPILER_TARGETS.md)
- [IR v1](IR_V1.md) and [IR specification](IR_SPEC.md)
- [C backend](C_BACKEND.md), [JavaScript backend](JS_BACKEND.md), and [bytecode VM](BYTECODE_VM.md)
- [Native runtime](NATIVE_RUNTIME.md) and [Termux guide](NATIVE_TERMUX.md)
- [Phase 4: path away from Python](PHASE4_ROADMAP.md)

## 3. PusingCuk AI

- [AI readiness and evidence boundaries](AI_ENGINE_READINESS.md)
- [Knowledge grounding](AI_KNOWLEDGE_GROUNDING.md)
- [Language evolution bridge](AI_LANGUAGE_EVOLUTION_BRIDGE.md)
- [Local AI service](AI_LOCAL_SERVICE.md)
- [Phase 6 repair-loop contract](PHASE6_PUSINGCUK_AI_REPAIR_LOOP.md)

PusingCuk AI is an assistant/orchestration layer over a selected model provider. It is not a project-trained foundation model. The repair-loop core is implemented, but its production provider, fixture-store, and full-matrix integrations must be treated as incomplete until the end-to-end path is wired and evidenced.

## 4. Security and operations

- [Phase 5 capability policy and VM budgets](PHASE5_CAPABILITY_SANDBOX.md)
- [Security policy](../SECURITY.md)
- [Offline adapters](OFFLINE_ADAPTERS.md)
- [Local studio](STUDIO_LOCALHOST.md)
- [Android distribution](ANDROID_DISTRIBUTION.md)
- [Tooling](TOOLING.md)

The language runtime is not an OS sandbox. A permission policy that is not called by a host operation does not mediate that operation. VM time and memory budgets are best-effort runtime checks, not hard operating-system limits.

## 5. Contribution, history, and audits

- [Contribution guide](../CONTRIBUTING.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Changelog](../CHANGELOG.md)
- [Repository structure](REPO_STRUCTURE.md)
- [Project status and roadmap](PROJECT_STATUS_AND_ROADMAP.md)

Audits, migration ledgers, dated reviews, and legacy documents are historical records unless explicitly revalidated. Do not copy an old score, fixture count, branch name, or readiness statement into a current claim without checking the current commit.

## Source-of-truth order

For a question about current behavior, use this order:

1. The implementation on the branch and commit being discussed.
2. The corresponding test and fixture definitions.
3. The latest successful CI run for that exact commit.
4. Generated compatibility reports tied to those fixtures.
5. Maintained specifications and contracts.
6. Roadmaps, dated audits, archives, and migration notes as historical context.

CI success proves only the checks that ran. File presence, documentation, a generated artifact, or an AI response is not proof of runtime correctness or production readiness.
