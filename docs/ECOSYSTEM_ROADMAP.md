# PusingCuk Ecosystem Roadmap

> This roadmap describes the implementation order and acceptance evidence. A listed component is not considered complete merely because its files exist.

## Product goal

Let a person describe an application in ordinary language, produce a supported `.cuk` program, verify its behavior, and receive a usable artifact with clear limits. The first delivery path must work with a browser and free repository automation; it must not depend on a paid API, hosted database, or always-on server.

## Architecture in plain language

1. **Language foundation — `.cuk`:** the language specification defines what a program means; the reference interpreter is the baseline; the compiler translates only supported constructs; the runtime and standard library provide repeatable behavior.
2. **Cuk Reality Engine:** runs canonical tests against the reference implementation and each claimed target, compares exit status/output/diagnostics to expected results, and reports unsupported behavior as unsupported rather than a pass.
3. **PusingCuk AI:** the user-facing assistant turns a request into a plan, asks for missing requirements, proposes `.cuk`, invokes only available/approved checks, and explains failures. It is not a model trained from scratch and must not invent verification results.
4. **Delivery surface:** the browser playground is the lowest-friction entry point. Downloadable projects and target-specific builds are offered only when that target has tested support.

## Milestones and acceptance gates

### M0 — Trustworthy repository baseline

- CI is triggered by every implementation and safety-critical launcher it tests.
- The complete required test suite is green on supported Python versions and native compilers.
- Vocabulary, specification-derived docs, canonical fixture IDs, and target manifests are checked for drift.
- Maintenance/evolution tools default to read-only dry-run behavior; tests cover their safety contract.
- Any failed check blocks a claim of completion.

**Exit evidence:** green GitHub Actions run on the exact commit being reported.

### M1 — Stable language contract

- Specify syntax, types/coercion, truthiness, evaluation order, scope, errors, I/O, and built-ins.
- Maintain one canonical conformance manifest and explicit target subsets.
- For each supported feature, test output, exit code, error category, and source location where applicable.
- Keep examples executable against the current contract; remove or replace broken examples rather than documenting them as working.
- Update the specification, tests, compatibility matrix, and user docs together.

**Exit evidence:** reference runtime and every claimed target pass the same applicable fixture set.

### M2 — Reliable compiler targets

- Define the shared intermediate representation and its invariants.
- Add a target only after its subset and unsupported cases are documented.
- Compare compiled execution with the reference runtime; successful compilation alone does not count as parity.
- Test generated artifacts and report platform/build requirements explicitly.

**Exit evidence:** per-target parity results with fixture IDs and no untested support claims.

### M2A — Self-hosting language tools

- Treat `examples/self_hosting/` as small, executable experiments, not proof that PusingCuk can compile itself.
- Grow the stages in order: token scanning from source text, parser and AST, evaluator/VM, stable IR, then code generation.
- Keep each stage runnable and covered by expected-output tests in the reference runtime before attempting cross-runtime parity.
- Add explicit module/import support and a stable host/runtime interface before splitting the compiler into reusable `.cuk` modules.
- Prove self-hosting only with a repeatable bootstrap: a trusted existing toolchain builds the `.cuk` compiler, and that compiler rebuilds itself with equivalent verified output.

**Exit evidence:** documented bootstrap procedure passes repeatedly in CI, with source/build hashes or equivalent reproducible evidence. Until then, describe the work as prototypes or partial self-hosting, never as a self-hosted compiler.

### M3 — Reality Engine

- Read canonical fixtures and target manifests instead of maintaining a second source of truth.
- Execute tests in bounded CI jobs with timeouts and captured output.
- Produce a machine-readable report of passed, failed, skipped, and unsupported cases, including the commit and target.
- Never describe a skipped test as a pass; never execute untrusted code as though the interpreter were an OS security sandbox.

**Exit evidence:** a reproducible report tied to a commit, with deliberately failing fixtures proving the engine detects mismatches.

### M4 — PusingCuk AI, offline-first prototype

- Begin with a deterministic browser workflow: user goal → structured requirements → supported template → generated `.cuk` → available validation → downloadable result.
- Show which requirements are satisfied, missing, or unsupported before claiming the app is complete.
- Use a local Ollama adapter on Termux only as an optional development path; test on the actual device before advertising device support.
- No automatic file mutation, Git push, secrets, or cloud API dependency by default.

**Exit evidence:** several end-to-end example requests produce repeatable artifacts and honest validation reports without a paid service.

### M5 — A usable public product

- Pick one narrow application category first, such as a local-first utility, instead of promising arbitrary apps.
- Provide examples, beginner instructions, error explanations, export/download, and a clear compatibility matrix.
- Validate on real browsers/devices, not CI alone.
- Add hosted services only when a concrete product requirement cannot be met locally and its cost/security model is understood.

**Exit evidence:** a person who does not know programming can follow the published flow, create an artifact, test it, and understand its limitations.

## What this means for the owner

No coding knowledge is required to review progress. Each milestone should be reported in plain language with: what changed, what a user can now do, the exact CI result, what remains unsupported, and a link to try it. Do not judge progress by commit count, file count, or the number of advertised compiler targets.

## Current status policy

The roadmap is a plan, not a completion badge. The authoritative status is the repository's current code, compatibility documentation, fixtures, and successful checks on the same commit. Device-specific behavior must be tested on-device; a Linux CI result is not proof of Termux or Android compatibility.
