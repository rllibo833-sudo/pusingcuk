# Pusingcuk Compiler Roadmap for the Three-Repository System

**Status:** Historical optional proposal; not a claim of production readiness or an active three-repository integration.

> **Current boundary (20 October 2026):** the owner reports that Founder-OS and CORE were deleted; GitHub API lookups for both repository endpoints returned 404. Reusable principles were selectively rewritten into PusingCuk-owned documents and code. This roadmap is retained for historical context only; do not treat its repository roles, cross-repo work, or future phases as active dependencies. Supabase resources and credentials have a separate retirement lifecycle.

> **Scope note:** This document describes one downstream three-repository integration scenario. It does not define the overall Pusingcuk mission, and contributors are not expected to target these repositories. The public project vision is in [VISION.md](VISION.md). All integration ideas below remain proposals until implemented, tested, and reviewed.

## Scope of this optional integration proposal

If this specific application project chooses to adopt Pusingcuk, it could explore a shared implementation language and compiler toolchain for these repositories:

- **Founder-OS / MEMORY:** durable decisions, constraints, review and recovery workflows.
- **kawasan-masjid-core / CORE:** canonical runtime, backend/data operations, evidence and economic truth.
- **kawasan-masjid-public / PUBLIC:** website experience, discovery and public-safe interactions.

These remain three distinct layers within that separate application project. A possible Pusingcuk integration would not collapse repository boundaries or make private CORE data public.

## Current truth

Pusingcuk currently has a Python reference pipeline, a native C runtime for a documented subset, a versioned AST-preserving IR v1, and an experimental C11 code-generation backend for a narrow integer subset. These components are not yet feature-equivalent. IR v1 is not executable bytecode. A backend invoked through Python is not yet a standalone multi-target compiler.

Do not migrate production logic or advertise full compiler support until tests demonstrate the required behavior.

## Confirmed readiness findings

- Native short-circuit behavior for `dan` and `atau` is now covered by shared fixtures: skipped operands must not trigger missing-variable or division-by-zero errors, while genuine syntax errors must still be reported.
- Native list equality now compares list contents recursively, including nested lists. Recursive comparison is bounded to protect the C stack; deeply nested/cyclic collection semantics remain a resource-limit edge that should be tested explicitly.
- Dictionary equality remains identity-based by design for now; do not assume it should become structural without a separate language design decision.
- Dictionary equality must be handled separately; do not assume it should become structural without a language design decision.
- The current conformance manifest is a useful but limited sample, not proof of full semantic parity. Test coverage must grow across precedence, scope, functions/returns, input limits, Unicode, numeric/range edges, malformed syntax, diagnostics and exit codes.
- CI on GCC/Clang does not replace a real Termux/Android device check. Building an Android APK does not prove all runtime paths have been exercised on-device.
- Native execution is not a sandbox; filesystem, network, database, process and secret access require explicit capability boundaries.

## Target architecture

`Pusingcuk source → lexer/parser → typed or validated semantic model → versioned IR → backend capability check → target code/artifact → target-specific tests`

The Python implementation remains the reference oracle during the transition. The native implementation and each backend must pass shared conformance fixtures before they are considered equivalent for a feature.

### Compiler interfaces

- Keep source syntax and canonical keyword meanings versioned.
- Give IR a schema version and deterministic serialization.
- Reject unsupported constructs with actionable diagnostics; never silently change semantics.
- Define a target capability manifest for each backend.
- Keep compiler/build tooling separate from the deployed runtime where possible.
- Provide reproducible build instructions and record compiler/toolchain versions.
- Treat generated artifacts as build outputs, not as source of truth.

## Phased plan and acceptance gates

### Phase 0 — Stabilize semantics

1. Keep native short-circuit behavior for `dan` and `atau` aligned with the reference runtime, including malformed syntax in skipped operands.
2. Keep list equality and nested-list semantics aligned with the reference; explicitly test the native recursion/resource boundary.
3. Expand shared fixtures for precedence, scope, functions/returns, input limits, Unicode, numeric/range edges, malformed syntax, diagnostics and exit codes.
4. Run conformance on GCC and Clang; test on real Termux/Android when device behavior matters.

**Gate:** no known high-priority semantic mismatch in the supported subset; CI must fail when parity fixtures fail.

### Phase 1 — Make IR a stable compiler contract

1. Specify every supported IR node, type/value representation, source location and versioning rule.
2. Validate malformed, oversized and unsupported IR inputs.
3. Add deterministic round-trip and compatibility tests.
4. Document which information is preserved and which transformations are permitted.

**Gate:** fixtures are stable across versions, and incompatible IR versions fail clearly.

### Phase 2 — Strengthen code generation

1. Expand C backend incrementally beyond the current narrow integer subset.
2. Add backend feature declarations and negative tests for unsupported syntax.
3. Test generated C with a supported C11 compiler and execute artifact-level tests.
4. Make build outputs reproducible and preserve source maps/diagnostic locations where feasible.

**Gate:** every advertised feature has compile, run, failure and regression tests.

### Phase 3 — Add another backend

Choose the next backend only after Phase 2 gates pass. JavaScript is a candidate for PUBLIC; C remains useful for native/CLI use. WebAssembly can follow once runtime, memory and host capability boundaries are defined. Do not promise all targets at once.

**Gate:** shared language fixtures pass for the target's declared feature subset, with documented differences or explicit unsupported errors.

### Phase 4 — Integrate one bounded capability at a time

Start with pure, deterministic, low-risk logic. Keep existing implementations as rollback paths. Use adapters at repository boundaries rather than importing internal code across repositories. Do not migrate database, filesystem, network, process, authentication or secret-handling paths until their capability and security contracts are reviewed.

**Gate per migration:** behavior parity, repository tests, security review for used capabilities, reproducible build, rollback proof and explicit approval from the maintainer responsible for the target application.

## Repository integration contract

| Repository | First candidates | Must remain outside the first migration |
|---|---|---|
| Founder-OS | Pure validation, normalization, deterministic decision-packet checks | Credentials, privileged automation, destructive operations and final Founder decisions |
| CORE | Pure calculations, schema-independent validation, deterministic transformation | Database writes, payment/acceptance state, secrets, external commitments and evidence authority |
| PUBLIC | Static content validation, route/content metadata, safe deterministic UI helpers | Authentication secrets, private CORE data and server-authoritative claims |

These are candidate areas, not commitments that the current code has already been converted.

## Security and governance

- Native execution is not a sandbox.
- Any filesystem, network, database or process access must be an explicit capability with least privilege.
- Never place credentials in source, generated artifacts, fixtures or logs.
- PUBLIC may expose only a verified public-safe subset of CORE information.
- Preserve the project rule: **No Proof, No Claim**.
- Coordinate changes with the maintainers of the target repositories and use their established review channels.

## Definition of success

Pusingcuk becomes the common language/toolchain when each repository can build and test its declared Pusingcuk modules reproducibly, target support is explicit, behavior is covered by shared conformance tests, and a failed migration can be rolled back safely. Success is measured by proven capabilities, not by replacing file extensions or merely adding Pusingcuk examples.
