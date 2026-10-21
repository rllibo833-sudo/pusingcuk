# Self-hosting state — canonical engineering handoff

This file is the single durable handoff for work toward a self-hosted .cuk compiler. Keep it synchronized with actual code on main; do not describe planned behavior as implemented.

## Source of truth and working rules

- main is the source of truth. Read the current files and commit before continuing work.
- SPEC.md defines the language contract. When implementation and spec disagree, record the gap and fix implementation or explicitly revise the contract.
- The goal is a compiler written in .cuk that can compile its own source and reproduce a usable compiler artifact without Python parsing or compiling the program.
- Do not ask the user to write code, open Termux, configure infrastructure, or run local commands.
- Do not create branches, PRs, daemon loops, speculative generated files, or test-only commits. Use existing tools to diagnose and validate changes. Keep each commit tied to a real implementation improvement.
- Update this file and README only when implementation/status actually changes.

## Verified architecture at last inspection

- examples/self_hosting/compiler.cuk contains a lexer, expression parser, statement parser, conditional/function handling, evaluator, and IR document emission for a limited subset.
- compiler/self_hosted_frontend.py constructs a wrapper around that .cuk source and runs it through pusingcuk_new.py. Python still hosts execution and validates the emitted IR. This is not a Python-free compiler.
- compiler/bootstrap.py calls from_source(source, source_name) for both stage 1 and stage 2. Matching hashes prove repeatability of the same host path, not a genuine second-stage compiler.
- Bootstrap evidence correctly reports status=reproducible-subset and full_self_hosting=false.
- A recent CI run reported errors for simple function/return coverage and for bootstrap compilation of that function. A conditional inside a function passed in that run. Do not mark the simple-function regression fixed until the existing CI run verifies it.
- The language frontend does not yet parse all of SPEC.md; in particular loops and collection/index forms remain incomplete on the self-hosted path.

## Existing tools to use (do not duplicate them)

- tools/diagnostic_repair_loop.py: deterministic lexer/parser diagnostics for files; it uses the reference Python lexer/parser, so it cannot by itself prove the self-hosted parser works.
- tools/reality_engine.py: fail-closed cross-runtime proposal acceptance and output comparison. Use it when the source is eligible for its manifest-backed fixture flow; never weaken its gates to force a pass.
- tools/differential_runner.py, tools/check_fixture_regression.py, and tools/ci_fixture_matrix.py: reuse for targeted regression/conformance evidence instead of inventing another runner.
- tools/evolve_language.py and tools/local_ai_adapter.py: proposal/AI helpers only. Do not start autonomous loops or allow them to push generated changes; human-reviewed deterministic patches remain the path.
- The existing native C backend and bytecode VM are potential execution targets, but a target backend passing fixtures does not make the source compiler self-hosted.

## Next implementation sequence

1. Use the self-hosted parser's actual failure token index (now surfaced in its error message) to isolate the simple function/return regression; fix the .cuk parser, not by routing that source to the Python canonical parser.
2. Reuse existing targeted CI/conformance checks to confirm simple fungsi, balek, and the conditional-function path. Do not add duplicate tests unless an existing check cannot express the required contract.
3. Extend the self-hosted program parser for the SPEC.md control-flow grammar (mumet/loop close) and then list/dictionary/index expressions, including correct IR v1 node serialization.
4. Change bootstrap so stage 1 produces a compiler artifact and stage 2 executes that artifact to compile the compiler source again. Compare generated compiler artifacts and run the result. Until this path works without Python doing source parsing/compilation, keep full_self_hosting=false.
5. Only after the implementation works, synchronize README, the compatibility/status docs, and this handoff.

## Completion criterion

Self-hosting is complete only when a .cuk-authored compiler builds a second compiler from the compiler's own source, the second compiler produces matching usable artifacts, and the result passes relevant conformance checks without the Python frontend/compiler path doing the compilation. Green CI or identical outputs from the same Python-hosted function are not sufficient.
