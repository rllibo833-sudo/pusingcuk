# Pusingcuk Documentation Index

Use this index to choose the right document. The current engineering baseline is the **Python reference interpreter + native C runtime**. Compiler and Android app prototypes remain documented, but they are not part of the baseline compatibility promise.

## Start here

- [Beginner guide](PEMULA.md) — first program, syntax basics, and guided examples.
- [Termux guide](termux/README.md) — run Pusingcuk on an Android phone without needing a desktop.
- [Project vision](VISION.md) — goals, community values, and current engineering priorities.
- [Repository structure](REPO_STRUCTURE.md) — where code, tests, tools, and documents live.
- [Contributor guide](../CONTRIBUTING.md) — changes, tests, and review expectations.

## Language specification and dictionaries

- [Complete language-reference map](language/README.md) — where to find keywords, aliases, built-ins, and language rules.
- [Built-in catalogue](language/BUILTINS.md) — full list of built-ins, argument counts, and support states for every target.
- [Language specification](../SPEC.md) — canonical syntax and intended behavior.
- [English technical dictionary](DICTIONARY.md) — shared terms for developers and reviewers.
- [Kamus Pusingcuk (Indonesian)](KAMUS_PUSINGCUK.md) — plain-language explanations.
- [Slang and alias registry guide](KOSAKATA_GENZ.md) — alias meanings and cultural context.
- [Language style guide](GAYA_BAHASA.md) — how the language and documentation should be expressed.
- [Machine-readable vocabulary registry](../library/kosakata.json) — keyword/alias metadata; not proof that every runtime supports each entry.

## Consistency and runtime support

- [Semantic contract](SEMANTIC_CONTRACT.md) — rules that implementations must follow.
- [Compatibility matrix](COMPATIBILITY.md) — which features are verified on which runtime.
- [Conformance fixtures](CONFORMANCE_FIXTURES.md) — how Python and native C behavior is compared, including common error classes, exit codes, and source lines.
- [Native C runtime](NATIVE_RUNTIME.md) — supported subset, limits, and build instructions.
- [Native Termux setup](NATIVE_TERMUX.md) — source build and installation details.
- [Android distribution/verification](ANDROID_DISTRIBUTION.md) — separates cross-build, emulator smoke test, and physical Termux validation.
- [Module system](MODULE_SYSTEM.md) — current import behavior and limitations.
- [Shared built-in contract](../library/README.md#builtin-contract-one-metadata-source) — machine-readable built-in metadata and update rules.

## Development and maintenance

- [Development/test gates](development/README.md) — expected commands and rules for claiming compatibility.
- [Independent review guide](INDEPENDENT_REVIEW.md) — structured technical review.
- [Tooling notes](TOOLING.md) — CLI and developer tools.
- [Offline adapters](OFFLINE_ADAPTERS.md) — status of integration experiments; not a claim of production-ready platform APIs.

## Security and audits

- [Security review guide](security/README.md) — threat boundaries, audit procedure, and security-related test expectations.
- [Official vulnerability-reporting policy](../SECURITY.md) — private reporting and current security limitations.
- [Native audit note](NATIVE_AUDIT_2026-10-11.md) — dated point-in-time findings, not a certification.
- [Native secure-ecosystem roadmap](NATIVE_SECURE_ECOSYSTEM_ROADMAP.md) — proposal, not a completed security milestone.

## Deferred experiments and future design

The documents below describe prototypes or possible future work. Read them only after understanding the Python/C baseline; their existence does not mean the corresponding target is stable or equivalent.

- [Compiler target status](COMPILER_TARGETS.md)
- [Compiler interoperability design](COMPILER_INTEROP.md)
- [IR v1](IR_V1.md)
- [Experimental C source backend](C_BACKEND.md)
- [Experimental JavaScript backend](JS_BACKEND.md)
- [Bytecode VM](BYTECODE_VM.md) and [PVM format](PVM_SPEC.md)
- [Compiler type system / standard-library notes](compiler-type-system-and-stdlib.md)
- [Android emulator smoke-test workflow](../.github/workflows/android-emulator-smoke.yml) — manual validation, separate from the core CI gate.
- [Android Studio prototype](ANDROID_STUDIO.md)
- [Local web workbench](WEB_WORKBENCH.md) and [Termux dashboard](TERMUX_DASHBOARD.md)
- [Three-repository compiler roadmap](THREE_REPO_COMPILER_ROADMAP.md)

## About the `library/` directory

The repository's `library/` directory contains examples, vocabulary metadata, the shared built-in contract, and internal runtime helpers. It is not yet a general package manager or a complete, importable standard library. Learner-facing vocabulary explanations are collected through the [language-reference map](language/README.md).

## Report a documentation mismatch

Include the document path, section, command, runtime (Python or C), observed result, and a minimal example. Do not post secrets or details of an unpatched vulnerability publicly; follow [SECURITY.md](../SECURITY.md).
