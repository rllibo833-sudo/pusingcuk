# Phase 6 — PusingCuk AI Repair Loop

**Status: evidence-gated loop core and an offline deterministic adapter are implemented; production integration remains incomplete.**

## Intended pipeline

Trusted repair request → proposed `.cuk` source → compiler diagnostics → trusted fixture evidence → complete differential matrix → acceptance or rejection.

A proposal is never evidence that a program is correct. Neither a model nor a rule engine may invent its own expected behavior.

## Implemented

- Provider-neutral `RepairAdapter.propose(request, current_source, diagnostics) -> str` interface.
- `compiler/offline_repair.py`: no-network, no-key, deterministic exact-substitution adapter. It accepts only a registered rule ID, requires exactly one source match, and rejects unknown, missing, or ambiguous matches.
- Injected compiler, fixture-runner, and differential-runner callbacks in `compiler/repair_loop.py`.
- Append-only JSON Lines attempt log with decision, gate outcomes, diagnostics, fixture identifier, and timestamp.
- Fail-closed acceptance: source must change, compile, have trusted fixture evidence, and pass a complete matrix with no regressions.
- Dry-run never accepts a proposal; the core does not write proposed source files.
- Unit tests cover loop gates and offline adapter matching/error behavior.

## What this does not provide

- The offline adapter is **not AI** and does not understand free-form Indonesian requests. It only applies maintainer-authored exact substitutions selected by rule ID.
- No real model/provider adapter is wired to this loop.
- The fixture callback is not yet connected to a trusted persistent fixture-creation workflow and canonical manifest update.
- The differential callback is not yet connected to a verified complete target matrix for the candidate change.
- No production caller persists accepted source, fixture, manifest, and generated evidence as one auditable change.
- The existing unit tests inject callbacks; they do not prove end-to-end production integration.

This approach allows safe, narrow, rule-based repair without API fees, while explicitly preserving the boundary between deterministic automation and AI.

## Required acceptance contract

1. Obtain expected behavior from a trusted request or maintainer; do not let a proposed patch define its own success criteria.
2. Compile the candidate and retain structured diagnostics.
3. Add a genuinely new fixture with stable ID, trusted expected output/exit status, and declared target support.
4. Run the canonical fixture suite and every required differential target against the same candidate state.
5. Reject if any required target is skipped, unavailable, incomplete, or regresses.
6. Persist source, fixture, manifest, and generated reports only after all gates pass; keep them in one auditable change.
7. Keep external providers optional. Never store API keys or credentials in source, prompts, fixtures, or logs.

## Security and audit limits

The JSONL log is an audit trail, not tamper-proof storage. Phase 5 VM controls are not an OS sandbox. Running untrusted code requires external OS/container isolation.

## Completion definition

Phase 6 remains incomplete until trusted fixture persistence, canonical full-matrix execution for the candidate change, fail-closed regression checks, and explicit source persistence are connected and demonstrated by an end-to-end CI test. A provider adapter is optional for the offline path; an AI-powered path would additionally require an actual model/provider.
