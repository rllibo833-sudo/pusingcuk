# PusingCuk AI Engine: readiness and knowledge migration

**Status:** roadmap and acceptance contract; not a claim that a production service is deployed.

## Current boundary

The maintained AI entry point is an experimental local-first CLI. It delegates inference to a selected provider (local Ollama by default, Gemini only by explicit opt-in), performs deterministic lexical retrieval over a small curated index, appends citations from validated source records, keeps active chat history in process memory, and offers a small allowlisted tool registry. Explicit project notes can be saved to the user's local memory store.

This is an application/orchestrator, not a foundation model trained by PusingCuk. It is not yet a multi-user HTTP service, and the language runtimes are not OS security sandboxes. Passing CI is evidence for the tested contracts only; it is not proof of production availability, general answer quality, or safe execution of arbitrary programs.

## Release gates

A release must not skip gates or turn a prototype into a production claim just because the code builds.

### Gate 0 — source and contract integrity

- All AI citations come only from validated immutable GitHub source envelopes.
- The curated runtime index contains reviewed PusingCuk-owned source paths only, has unique IDs, and pins each source URL to its exact path and commit.
- The index never crawls repositories, imports another repository at runtime, or treats retrieved text as instructions.
- The regression suite covers Indonesian retrieval, unrelated queries, source commit/path mismatch, invalid URLs, duplicate IDs, visibility, limits, and citation sanitization.
- Language-specific behavior remains owned by `SPEC.md`, `docs/SEMANTIC_CONTRACT.md`, builtin contracts, and executable conformance fixtures.

### Gate 1 — measurable answer quality and reliability

- Expand the 14-case exact-top-1 retrieval benchmark in small reviewed increments: ordinary Indonesian, colloquial wording/typos, ambiguous queries, questions outside the corpus, and security/policy questions.
- Record expected source IDs and whether a question is answerable. Measure retrieval top-1/top-3, unsupported-claim rate, citation precision, refusal behavior, and provider failure handling; publish the fixture set and result rather than saying "accurate" without evidence.
- Add regressions for prompt injection inside retrieved documents, fabricated URLs, malformed/oversized provider responses, timeouts, quota/rate-limit responses, and repeated/invalid tool calls.
- Model output is not proof that a requested tool ran. Tool outcomes must come from validated tool responses and their citations must retain the trusted source envelope.

### Gate 2 — explicit service contract before hosting

Before the CLI becomes an API, define and test a versioned request/response schema, health/readiness semantics, request IDs, cancellation/timeouts, bounded input/output, concurrent request limits, graceful shutdown, structured error codes, and streaming behavior. Keep provider-specific behavior behind an interface and do not silently retry non-idempotent tool operations.

A hosted service also needs authentication/authorization, abuse controls, per-user quotas, secret management, log redaction, privacy/retention controls, monitoring, backup/restore, dependency updates, rollback, and an incident procedure. Do not expose an unauthenticated model proxy or the local rule runner to the public internet.

### Gate 3 — safe deterministic rule execution

- AI may select only a named, versioned registered rule and schema-valid input. It must not submit source code, shell commands, paths, environment variables, or arbitrary capabilities for execution.
- Each rule manifest pins an immutable program identifier, language version, SHA-256, entry point, allowed capabilities, input/output schema, and resource limits.
- Determinism means the same normalized input and rule version produce the same result on each runtime claimed as supported. Cover boundary, invalid, overflow, and error cases with shared fixtures.
- Portability is claimed only for runtimes that pass the same required fixtures. Keep a truthful capability matrix; never equate Python reference, native C, transpilers, and PVM without conformance evidence.
- Before any untrusted-code feature is considered, require OS-level isolation, network denial, a read-only filesystem, least privilege, CPU/memory/process/output/time limits, and adversarial testing. The current project runtime is not a general sandbox.

### Gate 4 — small opt-in pilot

Start with a narrow, non-sensitive workflow and explicit human review. Define success, failure, latency, cost/quota, and rollback thresholds before collecting results. No customer, uptime, security, or production-readiness claims without observed evidence. Expand scope only after the previous gate is green.

## Gradually absorbing Founder OS and CORE knowledge

Founder OS and CORE are **reference sources for reviewed decisions and patterns**, not runtime dependencies. Their repositories must never be crawled wholesale. A migration entry should be added only after a maintainer has checked the primary document, determined that the information is relevant and safe to publish, and rewritten the transferable insight in PusingCuk's own words.

| Source area | Transferable subject | PusingCuk-owned destination | Acceptance evidence |
| --- | --- | --- | --- |
| Founder OS — durable decisions and boundaries | Decision status, explicit assumptions, ownership, provenance, and "No Proof, No Claim" discipline | AI policy/readiness docs and answer-grounding fixtures | Tests reject unsupported project claims and cite reviewed evidence |
| Founder OS — governance and recovery | Human approval for consequential actions, reversible operations, recovery notes with explicit opt-in | Assistant tool policy and local-memory tests | Unregistered/destructive actions fail closed; chat is not silently persisted |
| CORE — deterministic tool contracts | Named tools, version/hash pins, schema validation, bounded I/O, fail-closed behavior | `library/ai_tools.py`, rule manifests, runner tests | Invalid input/hash/version/capability never executes a rule |
| CORE — service operations and data boundaries | Authentication before actions, data minimization, auditable state transitions, no secret leakage | Future API/service layer; no import into current CLI merely for completeness | API contract, permission tests, secret-redaction tests, migration/restore evidence |
| CORE — masterplan/domain knowledge | Public-safe, factual domain material about Kawasan Masjid | Separate future domain corpus, not the language/engine index | Owner-reviewed source list and a domain-specific retrieval benchmark |

Do not copy code or lengthy document text from repositories unless its licensing and permissions clearly allow that. Prefer a short independently written summary with an immutable source citation, or independently implement the idea and test the behavior. Exclude credentials, private personal/financial material, unverified claims, and operational records from AI retrieval. A source citation proves where a claim came from; it does not prove the claim is true.

Each migrated source record must state: why it matters to PusingCuk, the exact immutable source path/commit, public-safe classification, the distilled principle, the test or acceptance check that makes it useful, and an owner for reevaluation. Remove a record if its evidence becomes obsolete or the acceptance test no longer holds. Keep the index curated and bounded.

## Conditions for retiring Founder OS and CORE

The public website is already a separate content site, but that does not establish that CORE's backend or data can be deleted safely. Before any repository is deleted (rather than merely archived), confirm all of the following:

1. No production deployment workflow, edge function, scheduled job, client, webhook, CI job, or maintainer runbook needs the repository.
2. Every required service has either been intentionally retired or moved with an owner and a tested rollback.
3. Required data has a verified export/backup, restore test, retention decision, and deletion plan; secrets are rotated or revoked where appropriate.
4. PusingCuk builds and tests with no runtime, index, or CI fetch dependency on Founder OS/CORE.
5. Unique decisions and proof records have been migrated as reviewed summaries, not wholesale copied.
6. The owner explicitly approves the final irreversible deletion after dependencies and retention are demonstrated.

Until these checks pass, prefer disabling retired endpoints explicitly and documenting remaining services over deleting repositories or stopping a shared backend project. Repository deletion does not itself delete separate cloud resources or data.

## Immediate acceptance target

For this phase, the acceptance target is a provenance-clean 14-source index, a non-contradictory grounding contract, automated local-only source assertions, and a documented release/migration gate. This narrows the next implementation step to measurable tests instead of claiming that the Engine is already production-ready.
