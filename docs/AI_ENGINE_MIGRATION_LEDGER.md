# PusingCuk AI Engine knowledge migration ledger

**Owner:** PusingCuk  
**Status:** reviewed conceptual migration; implementation evidence is tracked per rule/service below.  
**Purpose:** preserve useful governance and operational patterns without importing Founder-OS or CORE code, indexes, secrets, or runtime dependencies.

This ledger records why a pattern is being adopted, how it is rewritten for PusingCuk, and what evidence is still required. Source links are immutable historical references; runtime retrieval remains restricted to reviewed PusingCuk-owned documents in `library/knowledge_index.json`. No repository is crawled automatically.

## Migrated concepts

### 1. Local-first, replaceable inference provider

**Transferred principle:** prioritize a local model/provider first; treat model inference as a replaceable component, while PusingCuk owns its language semantics, runtime, rules and orchestration.

**PusingCuk interpretation:** the assistant is an application around Ollama by default or Gemini only when explicitly configured. Neither provider is the PusingCuk language, and neither implies that PusingCuk has trained a foundation model. Choosing Gemini sends prompts/context to a third-party service.

**Reference:** [Founder-OS local-first AI decision, commit d9a41ae](https://github.com/rllibo833-sudo/Founder-OS/blob/d9a41ae35dcc08628c7ac1fc38b3ac52fb982792/docs/LOCAL_FIRST_PUSINGCUK_AI.md).

**Evidence/status:** provider adapters and CLI are implemented; the authenticated HTTP adapter is loopback-only and experimental. Hosted deployment, per-user identity, abuse controls, monitoring, incident response and external security review remain open gates.

### 2. Human authority, evidence and truthful claims

**Rule:** No Proof, No Claim. Report users, customers, partners, revenue, production status and outcomes only when current evidence supports the exact claim.

**Transferred principle:** consequential external commitments stay behind explicit human review; reported outcomes must not exceed their evidence.

**PusingCuk interpretation:** model text is not proof that a tool ran or an outcome occurred. A citation establishes source provenance, not truth of every claim. Tools may execute only after registry and input validation; business decisions and irreversible actions must remain outside model-only authority until an authorized service enforces a human approval boundary.

**Reference:** [Founder-OS ownership and truth boundaries, commit 23421cb](https://github.com/rllibo833-sudo/Founder-OS/blob/23421cbd55c93d81b297b97d089638d85eb7a712/README.md).

**Evidence/status:** grounding and tool allowlist tests exist. The local chat service does not itself provide user identity, durable approval records or a production human-review workflow.

### 3. Registered deterministic rules, not model-generated code

**Transferred principle:** a business rule is a named, reviewed artifact with an immutable version/hash, schema-validated input, explicit capabilities and bounded results. Credentials and ambient authority are kept outside the rule runtime.

**PusingCuk interpretation:** the model can request only a registered tool. It cannot submit arbitrary `.cuk`, Python, shell or filesystem paths for execution. A rule is portable only between runtimes that pass the same conformance fixtures. A fixed artifact hash and deterministic output do not, by themselves, create an OS sandbox.

**References:** [CORE ownership and retirement contract, commit 2e11dd3](https://github.com/rllibo833-sudo/kawasan-masjid-core/blob/2e11dd3d8974a8a8390636a55a286057db99db05/SYSTEM_CONTRACT.md) and [PusingCuk rule-facing contract, commit 7645b8f](https://github.com/rllibo833-sudo/pusingcuk/blob/7645b8fa3b27a0304e42e51cf428cd05eb1297ff/docs/integrations/CORE_TOOL_CONTRACT.md).

**Evidence/status:** the reference Python and native C conformance suites plus fixed-rule fixtures cover selected pure rules. The native runtime is not an OS sandbox; arbitrary or untrusted programs must not be run with sensitive process permissions. A production isolated executor has not been established.

### 4. Migrate services and preserve data before shutting down repositories

**Transferred principle:** deleting a repository is not equivalent to retiring its deployed services. Inventory callers, functions, schedules, queues, webhooks, secrets and stored records; classify each resource as migrated, intentionally retired, or retained; test backup/restore and rollback before irreversible deletion.

**PusingCuk interpretation:** PusingCuk can become the canonical language/AI CLI without silently taking over CORE's database, payments, queues, identity or audit obligations. The public static website is independent, but the remaining CORE backend must be retired service-by-service. Founder-OS decision history is not deleted merely because a summary has been migrated.

**References:** [CORE retirement readiness checklist, commit 2e11dd3](https://github.com/rllibo833-sudo/kawasan-masjid-core/blob/2e11dd3d8974a8a8390636a55a286057db99db05/docs/RETIREMENT_READINESS.md) and [Founder-OS local-first migration gates, commit d9a41ae](https://github.com/rllibo833-sudo/Founder-OS/blob/d9a41ae35dcc08628c7ac1fc38b3ac52fb982792/docs/LOCAL_FIRST_PUSINGCUK_AI.md).

**Evidence/status:** a retirement checklist exists in CORE. Live callers, full data export/restore, credential rotation and explicit acceptance still need fresh verification before pausing the Supabase project or deleting source histories.

## Knowledge ingestion policy

1. Read one primary document at a time and record the exact immutable source commit/path.
2. Rewrite transferable ideas in PusingCuk's own words; do not copy entire indexes, files, private records, secrets or source code.
3. Keep the runtime knowledge index local-only. External references in this ledger provide provenance for the migration decision; they are not fetched as runtime dependencies.
4. For any behavior change, add a deterministic fixture/regression and identify the exact runtime versions that pass.
5. If source evidence, implementation or deployment status is missing, label it as a proposal or open gate—not as implemented or production-ready.

## Explicit non-goals

- This migration does not train a language model or transfer model weights.
- PusingCuk, native C, PVM and transpiled outputs are not a general-purpose security sandbox; never run untrusted code without independently reviewed OS-level isolation.
- It does not make CORE or Founder-OS safe to delete today.
- It does not claim hosted availability, real users, uptime, answer accuracy or a successful external outcome.

## Asset disposition and retirement gates — 2026-10-15

This is the current working disposition of old-repository assets. It is a migration record, not a claim that either source repository is already safe to delete.

| Source asset | Decision | Destination / proof | Exit condition |
|---|---|---|---|
| Founder-OS decisions, constraints, governance, and recovery records | Selectively distill; do not bulk-import raw memory | Keep only reviewed, relevant principles in this ledger or a PusingCuk-owned document. Preserve immutable source references when useful. | Inventory unique record IDs, export retained history, verify the export and rehearse restore; record what is intentionally not migrated. |
| Founder-OS local-first, human approval, and “No Proof, No Claim” principles | Adopt as architectural policy, not model training | Assistant system boundaries and this ledger; tool results and trusted citations remain separate from model claims. | Add or retain behavior-level tests for approval boundaries, citation integrity, and no silent memory writes. |
| CORE deterministic rule contracts, input/output schemas, hash pins, allowlists, bounded results, and fail-closed behavior | Re-implement as PusingCuk-owned code and fixtures where reusable | `library/ai_tools.py`, fixed reviewed `.cuk` artifacts, `tests/test_ai_tools.py`, and offline E2E coverage. | Each rule has a stable ID/version, hash, schema, explicit capability set, boundary fixtures, and verified CI evidence. |
| CORE's specific budget rule behavior | Keep the PusingCuk-owned `library/budget_threshold.cuk` as the AI tool artifact | Internal `ToolRegistry`; it no longer needs the legacy HTTP runner for assistant execution. | Continue only while its fixtures and source hash agree; the current executor is not an OS sandbox and must not run untrusted source. |
| CORE-hosted Edge Functions, database, queues, cron, payment/webhook handlers, notification workers, and audit/economic records | Do not copy automatically into PusingCuk. Classify each as migrate, explicitly retire, or retain outside PusingCuk. | No claim of equivalent replacement exists in the PusingCuk CLI/loopback HTTP adapter today. | Inventory callers and deployed resources, preserve required data, test restore, reconcile payment/idempotency contracts, rehearse rollback, and assign explicit ownership before decommissioning. |
| `tools/core-rule-runner.mjs` and its Docker sandbox harness | Legacy compatibility/regression harness, not assistant runtime | Still exercised by PusingCuk's security regression workflow and associated integration evidence. | Remove only after all consuming contract tests/workflows are migrated or intentionally retired and the replacement passes CI. Do not delete solely because `ToolRegistry` no longer calls it. |
| PUBLIC static Islamic/dakwah website | Keep independent; no PusingCuk AI runtime dependency | Its own repository/deployment remains the owner. | No action required for AI centralization unless a specific, approved content-grounding use case is introduced. |

### Current implementation evidence and limitations

- PusingCuk owns a curated, public-safe knowledge index with 16 source records in `library/knowledge_index.json`; runtime retrieval does not crawl CORE or Founder-OS.
- The local-first assistant has Ollama and Gemini adapters, bounded in-process chat history, explicit local memory, validated citation handling, a loopback-only HTTP adapter, and a small allowlisted `ToolRegistry`. This is an application around a replaceable model provider, not a foundation model trained by PusingCuk.
- Offline HTTP-to-rule E2E tests were added in `tests/test_ai_e2e.py` at commit `97482dc0aacc298f921a58e2654f5983ac1fadc4`; README's stale runner description was corrected at `c0592c3485455bb73f560a967534c4e6018181ca`. The connector does not currently expose push-triggered Actions run details here, so successful CI for those latest commits must not be inferred from the presence of the tests.
- The current fixed-artifact Python reference executor is explicitly not an OS sandbox. Hash pinning, allowlisting, and bounded I/O are useful safeguards but do not provide OS-level isolation for arbitrary code.

### Repository exit criteria

**Founder-OS may be archived only after** the required decision/history export is complete, its integrity is checked, restoration is rehearsed, every in-scope unique record is mapped or intentionally excluded, and the owner accepts the preserved-history plan.

**CORE may be archived only after** every deployed service and caller has an explicit disposition, required operational/audit/economic data is exported and restore-tested, payment/webhook/queue behavior is migrated or intentionally retired with tests, credentials are rotated/revoked where appropriate, and deployment/CI/operator paths no longer require CORE.

Repository deletion is a separate, later decision. An archive must preserve the evidence and rollback point; deleting GitHub source does not itself retire deployed Supabase resources or erase their data.

