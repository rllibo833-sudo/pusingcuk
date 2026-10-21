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
- The repository already contains a reference interpreter, IR v1, bytecode VM, native C runtime, experimental multi-target backends, module resolver, local AI adapter/service, Reality Engine, browser playground, Android Studio shell, and application examples. Do not recreate these surfaces as roadmap work; integrate and reuse them where their contracts fit.
- `source_lexer.cuk` now contains a limited multiline parser for `lah name = expression`, `name = expression`, and `hedeh expression`, plus an AST evaluator with a local variable environment. Runtime tests cover reassignment, downstream value flow, rejection of assignment to an undeclared name, and malformed declarations. Its tested expression subset includes precedence, parentheses, unary minus and modulo. This remains a staged frontend prototype, not a self-hosted compiler: control flow, blocks, functions/calls, full diagnostics, IR lowering, and bootstrap are not implemented.
- Each grammar increment needs positive and negative tests, expected-output regressions, and explicit unsupported-syntax notes. Keep the Python reference frontend as an oracle until the self-hosted frontend matches applicable conformance fixtures.
- Reuse IR v1 and the bytecode VM only after a tested mapping from the self-hosted AST to the existing IR/bytecode contracts; do not create a parallel format without a compatibility reason.
- Define one tested module/import contract before splitting the compiler into reusable `.cuk` modules.
- **Bootstrap in plain language:** first use the existing compiler to build the new compiler from its `.cuk` source; then use that new compiler to build itself again; compare outputs and run the same conformance suite. Repeat this in CI. It is not complete until this process works repeatedly on the same commit.

**Exit evidence:** a real program parser and compiler pipeline, followed by a repeatable bootstrap job in CI with source/build hashes or equivalent reproducible evidence. Until then, describe the work as prototypes or partial self-hosting, never as a self-hosted compiler.

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


## Catatan implementasi self-hosting — 2026-10-21

Prototipe `examples/self_hosting/source_lexer.cuk` kini menambahkan parsing struktur program multi-baris terbatas untuk deklarasi `lah nama = ekspresi` dan pernyataan `hedeh ekspresi`. Ini menghasilkan node statement, tetapi belum menyelesaikan referensi nama, eksekusi program penuh, kontrol alur, IR lowering, atau bootstrap. Tes referensi mengunci output dan status parser; jangan menafsirkan ini sebagai compiler mandiri.

Arsitektur penggunaan lokal tetap **Android + Termux sebagai adapter/data center lokal** untuk PusingCuk AI dan Cuk Reality Engine. Perubahan toolchain tidak boleh menghapus, mereset, memigrasikan secara destruktif, atau mengubah endpoint/config matrix lokal secara diam-diam. Ollama tetap opsional untuk tes inti; provider lokal harus eksplisit loopback, dan proposal evolusi tetap review-only tanpa commit/push otomatis.


## Increment self-hosting terbaru — 2026-10-21

Parser program prototipe kini membentuk node `VARIABLE` untuk identifier dalam ekspresi dan evaluator menerima lingkungan variabel. `jalankan_program` menjalankan deklarasi dan mengumpulkan output `hedeh`, sehingga contoh multi-baris mendeklarasikan `x` lalu mencetak nilainya. Cakupan tetap terbatas pada integer/ekspresi aritmetika dan statement `lah`/`hedeh`; belum mendukung assignment ulang, kontrol alur, fungsi, lowering ke IR v1, atau bootstrap. Tes runtime membuktikan variabel lintas statement dan penolakan deklarasi malformed; kontrol alur, assignment ulang, IR lowering, serta bootstrap tetap belum selesai.

Untuk penggunaan lokal, HP Android + Termux tetap adapter/data center PusingCuk AI dan Cuk Reality Engine. Perubahan ini hanya menyentuh prototipe dan dokumentasi; jangan reset/migrasi matrix lokal atau mengubah endpoint/provider. Ollama tetap opsional untuk core CI, tidak ada fallback cloud diam-diam, dan evolusi AI tidak melakukan commit/push otomatis.


## Self-hosting increment — 2026-10-21 (assignment)

The limited program parser now emits `ASSIGN` statement nodes. The runner tracks declared names and rejects assignment to undeclared names with an explicit runtime status. Tests exercise `x = x + 4`, verify the changed value flows to later expressions, and cover an undeclared assignment failure. This is still not a compiler or bootstrap proof; the AST is not yet lowered to IR v1/bytecode VM.


## Self-hosted codegen slice — 2026-10-21

The `.cuk` codegen example now recursively emits nested integer/binary AST nodes as a C expression and explicitly rejects unsupported operators. The fixture tests nested precedence structure and the rejection path. This does not yet constitute a cross-language compiler: the example still receives a hand-built AST and is not wired to the canonical parser, IR v1, bytecode VM, or target backends. The next integration milestone is a common source-to-IR path with parity tests across the existing backends.


## CI correction — 2026-10-21

The nested codegen fixture was updated to expect the actual recursive output (`long hasil = (7 + (5 * 6));`) and the explicit `UNSUPPORTED_OPERATOR` result. The first core run caught a stale assertion from the previous flat-expression demo; the generator behavior itself matched the new fixture. The core suite must be rerun on the correction commit before this increment is considered green.
\n\n### Increment target lintas bahasa — Rust (2026-10-21)\n\nA first Rust source backend is wired into the existing IR v1 CLI. Its declared subset is numeric literals, variables, reassignment, output, unary minus, and `+ - * / // %`; unsupported nodes fail closed. This is a narrow sixth language target, not full Rust compatibility or a claim of 10-language support. Tests lock generated source and rejection behavior; compiler/runtime parity must be expanded before the target subset is advertised as conformant.\n