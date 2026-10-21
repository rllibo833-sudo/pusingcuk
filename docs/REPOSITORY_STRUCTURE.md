# Repository structure and ownership

This document defines where new work belongs. Existing root-level compatibility modules are retained until packaging/import references can be migrated and tested as one change.

## Canonical ownership

- `compiler/`: compiler front-end integration, IR orchestration, target backends, and VM.
- `pusingcuk/`: language package and public runtime-facing API.
- `library/`: builtin contracts, vocabulary registries, adapters, and language data.
- `tools/`: maintenance utilities, conformance/evolution tooling, diagnostics, and developer automation. These tools must be safe by default; evolution proposals remain review-only unless an explicitly tested transaction is invoked.
- `tests/`: unit tests, conformance fixtures, manifests, and target-specific parity tests.
- `examples/`: runnable teaching programs only. Examples must be tested against the current language contract.
- `docs/`: authoritative explanations of behavior and current target support.
- `native/`: native C runtime and build inputs.
- `site/`, `web/`: public website and browser playground assets.

## Root-level compatibility policy

The root still contains Python modules listed in `pyproject.toml` under `tool.setuptools.py-modules`. Do not move those modules until all imports, packaging metadata, command entry points, workflows, and tests are migrated together. Do not add new implementation modules to the root.

Maintenance scripts are moved into `tools/` when their imports and path assumptions have been audited. The legacy root launcher may remain as a thin compatibility shim, but it must not duplicate implementation logic.

## Conformance is the acceptance gate

The canonical fixture identities and expected behavior live in `tests/conformance/manifest.json`. Target-specific manifests may select a subset, but they must reference IDs from the canonical manifest and may not redefine expected results.

A fixture passes only when the process exit code, stdout, error class, and source line (for expected errors) match the canonical expectation. A successful compile alone is not a pass. A matching failure is only a pass for a fixture whose manifest explicitly expects that same failure. Unlisted fixture IDs are unsupported/not claimed, never implicitly passing.

Before changing language semantics:
1. Add or update a minimal fixture and its stable ID.
2. Update the canonical expectation only when the language contract itself intentionally changes.
3. Run the reference and every target claimed by that fixture.
4. Record target support explicitly; never infer support from another backend.
5. Run unit tests, native tests, conformance, and docs synchronization before merge.
6. Update the relevant documentation in the same scoped change.

## No-overlap rules

- One branch/PR per cohesive change; no broad replacements across the repository.
- Do not create a second authoritative manifest or duplicate test suite.
- Preserve public launchers while migrating imports; remove compatibility shims only in a separately verified breaking-change cycle.
- Do not bypass failed or skipped required checks, and do not claim unexecuted targets as verified.
