# PusingCuk Documentation Map

This documentation is organized around reader needs rather than the order in which files were created. Dated audits and experimental notes remain useful as history, but they do not automatically describe current feature status.

## 1. New to PusingCuk?

1. [Main README](../README.md) — short overview and how to run a program.
2. [Beginner guide](PEMULA.md) — basic syntax and examples (Indonesian).
3. [Warung-language dictionary](KAMUS_PUSINGCUK.md) — keywords, functions, technical terms, and repository map (Indonesian).
4. [Examples index](../examples/README.md) — available programs.

## 2. Language rules and library

- [Language specification](../SPEC.md) — user-visible syntax and behavior.
- [Semantic contract](SEMANTIC_CONTRACT.md) — behavior that must be testable.
- [Built-ins](language/BUILTINS.md) and the [machine-readable built-in contract](../library/builtin_contract.json).
- [Gen Z/Gen Alpha vocabulary](KOSAKATA_GENZ.md) and [language style](GAYA_BAHASA.md).
- [Repository structure](REPO_STRUCTURE.md).

## 3. Compiler, runtime, and compatibility

- [Compatibility matrix](COMPATIBILITY.md) — support limits for each implementation.
- [Conformance fixtures](CONFORMANCE_FIXTURES.md) — behavior covered by tests.
- [Compiler targets](COMPILER_TARGETS.md), [IR v1](IR_V1.md), [C backend](C_BACKEND.md), [C++17 target](COMPILER_TARGETS.md#arti-target-keluar), [JavaScript backend](JS_BACKEND.md), and [bytecode VM](BYTECODE_VM.md).
- [Native runtime](NATIVE_RUNTIME.md) and [Termux guide](NATIVE_TERMUX.md).
- [Tooling](TOOLING.md) and [editor support](EDITOR_SUPPORT.md).

## 4. PusingCuk AI and integrations

- [AI engine readiness](AI_ENGINE_READINESS.md).
- [AI knowledge grounding](AI_KNOWLEDGE_GROUNDING.md).
- [Language evolution bridge](AI_LANGUAGE_EVOLUTION_BRIDGE.md).
- [Local AI service](AI_LOCAL_SERVICE.md).
- [Project overview](PROJECT_OVERVIEW.md).

The presence of an AI module or adapter does not prove a self-trained model, general quality, or production-ready SaaS. Claims must be tied to tests and configuration that actually exist.

## 5. Development status, contribution, and security

- [Canonical status and v1.0 roadmap](PROJECT_STATUS_AND_ROADMAP.md) — the only active roadmap.
- [Development issue backlog](development/ISSUE_BACKLOG.md) — unfiled issue drafts; verify against current code before opening an issue.
- [Repository structure](REPO_STRUCTURE.md) — canonical directory map.

## 6. Contribution, security, and historical notes

- [Contribution guide](../CONTRIBUTING.md).
- [Security policy](../SECURITY.md).
- [Code of Conduct](../CODE_OF_CONDUCT.md).
- [Changelog](../CHANGELOG.md).

Dated audits, roadmaps, archives, and migration notes should be treated as historical context unless their status is re-verified. For compatibility claims, prioritize the specification, contract, implementation, fixtures, and CI results from the same commit.

## Security note

The interpreter, compiler, and VM are not an operating-system sandbox. Do not run untrusted code in sensitive environments. A green CI run proves only the jobs that actually ran.
