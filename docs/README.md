# Pusingcuk Documentation Index

This directory contains the project's guides, language contracts, implementation notes, compatibility records, and roadmaps. The Python interpreter is the reference development path; native and compiler targets support documented subsets and remain experimental.

## Start here

- [Beginner guide](PEMULA.md) — learn the language with small runnable examples.
- [Language and technical dictionary (English)](DICTIONARY.md) — shared terminology for contributors and reviewers.
- [Plain-language dictionary (Indonesian)](KAMUS_PUSINGCUK.md) — Indonesian explanations of technical terms.
- [Language style guide](GAYA_BAHASA.md) — writing style and terminology principles.
- [Project vision and community principles](VISION.md) — project goals and contribution values.
- [Independent review guide](INDEPENDENT_REVIEW.md) — review scope, commands, and known limitations.

## Language reference and semantics

- [Slang and alias guide](KOSAKATA_GENZ.md)
- [Semantic contract](SEMANTIC_CONTRACT.md)
- [IR v1](IR_V1.md)
- [Module system notes](MODULE_SYSTEM.md)
- [Conformance fixtures](CONFORMANCE_FIXTURES.md)

The root [language specification](../SPEC.md) is the primary syntax reference. If documentation conflicts with observed behavior, report the mismatch and use implementation plus reproducible tests to determine the current behavior.

## Runtime and compiler architecture

- [Repository structure](REPO_STRUCTURE.md)
- [Compiler interoperability](COMPILER_INTEROP.md)
- [Compiler targets](COMPILER_TARGETS.md)
- [Python importer and allow-listed standard-library APIs](IMPORT_PYTHON.md)
- [Compiler type system and standard-library notes](compiler-type-system-and-stdlib.md)
- [Bytecode VM](BYTECODE_VM.md)
- [PVM specification](PVM_SPEC.md)
- [C backend](C_BACKEND.md)
- [JavaScript backend](JS_BACKEND.md)
- [Native runtime](NATIVE_RUNTIME.md)
- [Native parity audit](NATIVE_PARITY_AUDIT.md)

## Platform and developer tooling

- [Compatibility matrix](COMPATIBILITY.md)
- [Android Studio](ANDROID_STUDIO.md)
- [Native Termux guide](NATIVE_TERMUX.md)
- [Termux dashboard](TERMUX_DASHBOARD.md)
- [Tooling notes](TOOLING.md)
- [Web workbench](WEB_WORKBENCH.md)

## Security, audits, and roadmaps

- [Security policy and reporting](../SECURITY.md)
- [Native audit, dated 2026-10-11/12](NATIVE_AUDIT_2026-10-11.md)
- [Native secure ecosystem roadmap](NATIVE_SECURE_ECOSYSTEM_ROADMAP.md)
- [Three-repository compiler roadmap](THREE_REPO_COMPILER_ROADMAP.md)

Audit notes are point-in-time engineering records, not certifications. Check their stated commit/date and verify claims against the current default branch before relying on them.

## Vocabulary registry and examples

The machine-readable vocabulary registry and selected examples live in [the library directory](../library/README.md). That registry is a contributor aid, not proof that every alias or feature is supported by every runtime.

## How to report a documentation problem

When reporting a mismatch, include the document path, the relevant heading, the runtime or backend involved, the exact command used, and a minimal reproducible example where possible. Do not include passwords, tokens, private data, or details of an unpatched security issue in a public report; follow [SECURITY.md](../SECURITY.md) for security concerns.


- [Shared builtin contract](../library/README.md#builtin-contract-one-metadata-source)
