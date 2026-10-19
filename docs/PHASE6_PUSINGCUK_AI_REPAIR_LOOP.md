# Phase 6 — PusingCuk AI Repair Loop

Status: **provider-neutral repair-loop core implemented; production callbacks must still be wired to the repository's real fixture store and complete differential matrix.**

## Acceptance contract

Request → proposed \`.cuk\` source → compiler diagnostics → new fixture → complete differential matrix → decision. Model output is a proposal, never proof.

A changed proposal is accepted by the core only when compilation succeeds, the fixture callback confirms a newly added fixture, and the differential callback returns \`complete: true\`, \`ok: true\`, and an empty \`regressions\` list. Missing/partial results fail closed. Every attempt is appended to JSON Lines, including adapter errors, rejected proposals, and dry runs.

Dry-run can execute validation callbacks but always returns \`accepted=false\`; this core never writes source files. The trusted caller must persist a source explicitly after receiving an accepted result.

## Provider adapter

Implement \`RepairAdapter.propose(request, current_source, diagnostics) -> str\` for any model/provider. Compiler, fixture, and differential execution are injected callbacks, keeping the loop model-agnostic.

The fixture callback must return \`{"added": true, "fixture_id": "..."}\` only after persisting a genuinely new fixture. The differential callback must return \`{"complete": true, "ok": true, "regressions": []}\` only after the entire required matrix has run. Never map skipped or partial work to success.

## Current limits

- No provider is bundled and no self-trained model is claimed.
- The repair loop is not yet connected to a production model adapter or the repository's canonical full-matrix runner; callers must supply these callbacks.
- The JSONL log is an audit trail, not tamper-proof storage.
- Phase 5 VM policy is not an OS sandbox; untrusted execution needs external OS/container isolation.
