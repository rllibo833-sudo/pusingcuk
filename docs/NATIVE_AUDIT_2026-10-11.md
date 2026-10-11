# Native Pusingcuk Audit — 2026-10-11

**Status:** Source-level audit in progress. This report does not certify security or complete compiler readiness.

## Scope inspected

- Native C source and CLI entry point
- Modular Python lexer/parser/AST/evaluator pipeline
- Native runtime support matrix
- Semantic contract and compiler/IR documentation
- Manifest-driven cross-runtime conformance runner
- GitHub Actions coverage for Python, native GCC/Clang, conformance, and Android debug APK build
- Beginner and Gen Z/Gen Alpha language guidance

## Architecture status: distinguish three things

| Component | Verified role | Important limitation |
|---|---|---|
| Modular Python path | Reference implementation through lexer, parser, AST, evaluator, CLI | Requires Python to run this path |
| Native C runtime | Parses and executes a bounded subset directly; built executable can run that subset without Python | It is not a complete compiler and does not yet support the full language |
| IR v1 + C code-generation backend | IR v1 validates an AST-preserving JSON representation; C backend emits C11 for a narrow integer subset | IR is not executable bytecode; backend is experimental and invoked through Python |

Do not describe Pusingcuk as a complete, general-purpose native compiler yet. Accurate phrasing: **experimental language with a Python reference pipeline, a standalone native C runtime for a tested subset, a versioned AST-preserving IR, and an experimental C code-generation backend.**

## Confirmed finding — P1 semantic parity

The native runtime's and_expr() and expr() functions evaluate the right operand before applying logical truthiness. The semantic contract explicitly requires short-circuit evaluation.

Expected behavior:

- `salah dan variabel_yang_belum_ada` evaluates to false without looking up the missing variable.
- `benar atau variabel_yang_belum_ada` evaluates to true without looking up the missing variable.
- Syntax errors in source text must still be diagnosed even when a logical operand is not evaluated.

Tracking issue: https://github.com/rllibo833-sudo/pusingcuk/issues/44

**Acceptance gate:** add manifest fixtures; fix the native parser/evaluator architecture without hiding genuine syntax errors; run them against reference and native runtimes; require CI on GCC and Clang. Until then, the native and reference runtimes are not semantically equivalent.

## Coverage and confidence

- CI does test Python unit tests, native runtime tests under GCC/Clang, a manifest-driven conformance suite, and Android debug APK compilation.
- The current manifest has seven shared conformance cases. It is useful but not sufficient to prove full parity.
- The runtime support matrix documents important boundaries: no native module system, bounded collections/text, restricted native string indexing, and finite function/call limits.
- Android APK compilation does not prove that the native executable has been exercised on a real Android/Termux device.
- Passing tests only establish behavior covered by those tests. They do not establish sandboxing, independent security review, or production readiness.

## Next audit and implementation priorities

1. Fix short-circuit semantics with cross-runtime positive and negative fixtures.
2. Expand conformance around operator precedence, boolean short-circuiting, malformed syntax, variable/function scope, returns, input limits, collection boundaries, numeric edge cases, and diagnostic/exit-code behavior.
3. Compare reference and native semantics for equality and collection identity, UTF-8 handling, numeric/range behavior, and error cases. Record each confirmed gap with a minimal reproducer.
4. Improve error messages to show file, line, column, cause, and a practical fix hint where possible.
5. Keep canonical keywords stable. Optional slang aliases must normalize to the same canonical tokens; do not add aliases solely to chase trends.
6. Provide a one-minute quickstart, copy-paste examples, expected output, mini-challenges, and a beginner-to-advanced path. Keep technical explanations precise enough for professional developers.
7. Separate compiler milestones from runtime milestones: semantic analysis, module/import resolution, executable IR/bytecode or clearly scoped native code generation, backend feature checks, reproducible artifacts, and artifact-level tests.
8. Design filesystem, network, database, process, and secret access as explicit capabilities with minimum privileges. Native execution is not a sandbox.
9. Verify actual device behavior in Termux and test the Android app's execution path, not only its build.
10. Integrate only one pure, low-risk CORE function after the required features and parity tests are demonstrated. Keep CORE as rollback path.

## Product-language rule

The target is **easy to start, serious enough to grow**:

- Beginner mode: plain Indonesian, small examples, one concept per lesson, immediate expected output.
- Builder mode: clear CLI, examples, test runner, formatter/linter over time, readable diagnostics.
- Expert mode: formal spec, deterministic semantics, versioned IR, explicit runtime capabilities, testable backends.
- Gen Z/Gen Alpha style: friendly and optional. Avoid forced slang, rapidly expiring memes, or slang-only error messages.

## Exit criteria for replacing CORE components

Do not replace or delete CORE because the native executable builds. Require a capability matrix, required cross-runtime fixtures, an integration contract, security review for used capabilities, reproducible builds, tests in CORE, backup/rollback proof, and explicit Founder approval.


## Additional confirmed parity risk — collection equality

The native C equality helper compares LIST and DICT values by pointer identity, while the reference evaluator delegates to language/container equality. Structurally equal collections may therefore produce different results across runtimes.

Tracking issue: https://github.com/rllibo833-sudo/pusingcuk/issues/46

Acceptance gate: run a reproducer against the reference CLI, decide/document nested collection semantics, add shared success/failure fixtures, and require native/reference parity in CI.
