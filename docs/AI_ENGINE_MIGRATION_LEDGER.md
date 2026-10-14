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
- It does not make PusingCuk, native C, PVM or transpiled output a general-purpose security sandbox.
- It does not make CORE or Founder-OS safe to delete today.
- It does not claim hosted availability, real users, uptime, answer accuracy or a successful external outcome.
