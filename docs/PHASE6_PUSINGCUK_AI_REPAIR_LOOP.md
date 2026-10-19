# Phase 6 — PusingCuk AI Repair Loop

**Status: repair-loop core implemented; end-to-end production integration is incomplete.**

## Intended pipeline

Request → proposed `.cuk` source → compiler diagnostics → a new, behavior-specific fixture → complete differential matrix → acceptance or rejection.

Model output is an untrusted proposal, never evidence that a program is correct.

## Implemented core

- Provider-neutral `RepairAdapter.propose(request, current_source, diagnostics) -> str` interface.
- Injected compiler, fixture-runner, and differential-runner callbacks.
- Append-only JSON Lines attempt log containing the decision, gates, diagnostics, fixture identifier, and timestamp.
- Fail-closed acceptance: the proposal must change the source, compile successfully, add a fixture, and pass a complete matrix with no regressions.
- Dry-run always returns `accepted=false`; the core does not write proposed source files.
- Unit tests cover acceptance, unchanged proposals, compiler failures, missing fixtures, regressions, incomplete matrices, dry-run logging, and adapter exceptions.

## What is not yet integrated

- No production model/provider adapter is wired to this loop.
- The fixture callback is not connected to the repository's canonical manifest and persistent fixture store.
- The differential callback is not connected to a verified full matrix that includes every required target for the changed behavior.
- No trusted caller currently persists an accepted source as part of a complete production workflow.

Therefore Phase 6 must not be marked complete just because its unit tests or CI pass.

## Acceptance contract for production integration

1. Obtain an explicit expected behavior from a trusted request or maintainer; never let the model define its own success criteria.
2. Compile the proposal and preserve structured compiler diagnostics.
3. Create and persist a genuinely new fixture with a stable identifier, expected output/exit status, and declared target support.
4. Run the canonical fixture suite and the complete required differential matrix against the same candidate commit/worktree.
5. Reject the proposal if any required target is skipped, unavailable, regresses, or produces an incomplete result.
6. Record the result and persist source changes only after every gate passes. Keep the source, fixture, manifest, and generated reports in the same auditable change.
7. Use a provider adapter only for proposal generation; never put API keys or service credentials in source, prompts, fixtures, or logs.

## Security and audit limits

The JSONL log is an audit trail, not tamper-proof storage. Phase 5 VM controls are not an OS sandbox. Running untrusted code requires external OS/container isolation.

## Completion definition

Phase 6 is complete only when a real provider adapter, trusted expected-behavior input, persistent fixture creation, canonical full-matrix execution, fail-closed regression checks, and explicit source persistence are connected and demonstrated by CI or another reproducible integration test. Until then, label the work **core implemented; integration pending**.
