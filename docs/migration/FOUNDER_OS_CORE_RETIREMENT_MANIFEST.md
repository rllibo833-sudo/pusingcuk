# Founder-OS and CORE transfer manifest

**Destination owner:** PusingCuk  
**Snapshot date:** 2026-10-15  
**Purpose:** record the selected knowledge that has been transferred, deliberately excluded assets, and the remaining service/data disposition.  
**Important:** this manifest is not itself a backup, a restore test, or authorization to delete cloud data.

## Transfer scope and ownership

| Source | Original responsibility | Disposition in PusingCuk |
|---|---|---|
| Founder-OS | Durable decisions, accepted constraints, strategy rationale, lessons, recovery context | Transfer the stable rules into `docs/ai/DECISION_AUTHORITY_AND_EVIDENCE.md`; use exact source provenance. Do not bulk-copy raw memory files. |
| Founder-OS local-first AI decision | Separate inference provider from language/runtime; prefer local inference; evidence-gated migration | Transfer to `docs/ai/LOCAL_MODEL_AND_RULE_SAFETY.md`; local Ollama remains default and Gemini remains opt-in. |
| Founder-OS decision protocol | Human authority, explicit review outcomes, traceable follow-up | Transfer to `docs/ai/DECISION_AUTHORITY_AND_EVIDENCE.md`. |
| Founder-OS generic-SaaS decision | Keep architecture platform-ready without letting a generic SaaS starter define the project | Transfer as product/strategy discipline in the evidence contract. |
| Founder-OS/CORE masterplan and operating model | Conceptual Islamic eco-city vision, digital-first proving strategy, economic constraints, source/evidence process | Distilled into `docs/knowledge/KAWASAN_MASJID_MASTERPLAN_AND_OPERATING_MODEL.md`; historical metrics remain explicitly marked as targets or concepts. |
| CORE rule/tool interface and relevant security policy | Registered deterministic rules, source hash/schema/capability boundary, fail-closed behavior | The implementation contract and existing pure-rule tests remain PusingCuk-owned. The safety rules are synthesized in `docs/ai/LOCAL_MODEL_AND_RULE_SAFETY.md`. |
| CORE AI worker, queue, API, notification, payment, revenue, review, SQL migrations, deployment workflows | Hosted operations, authorization, operational/audit data, and externally callable service endpoints | **Not copied wholesale into PusingCuk.** No real users or active collaboration were reported by the owner; current live counts below show no inquiries or orders. These services are candidates for retirement, not capabilities that the experimental local CLI silently replaces. |
| CORE/PUBLIC boundary | Public site is an independent static Islamic/dakwah content site | Keep PUBLIC separate; no new runtime dependency is introduced by this migration. |

## Immutable source snapshots

- Founder-OS main at transfer: [`e3a9893ca3e8d64182e33b71f5360822b176fe51`](https://github.com/rllibo833-sudo/Founder-OS/commit/e3a9893ca3e8d64182e33b71f5360822b176fe51).
- CORE main at transfer: [`9f24694b17c28b561069b1391922b3c4816842fb`](https://github.com/rllibo833-sudo/kawasan-masjid-core/commit/9f24694b17c28b561069b1391922b3c4816842fb).
- PusingCuk base before this transfer: [`7dbbcf20d21679241a12bff019c496a0a94993c4`](https://github.com/rllibo833-sudo/pusingcuk/commit/7dbbcf20d21679241a12bff019c496a0a94993c4).

The source links are provenance for the transfer, not ongoing runtime dependencies. The PusingCuk retrieval index points only to PusingCuk-owned documents.

## Live Supabase inventory observed on 2026-10-15

Project: `Kawasan-mesjid-1000ha`, ref `lnpzgrodwnhthcwudebk`, region `ap-southeast-2`, status `ACTIVE_HEALTHY`.

Last read-only verification: `2026-10-14T21:56:18Z` (2026-10-15 05:56:18, Asia/Makassar); **54 applied migration-history rows**.

### Schedules

| Job | Schedule | Observed state | Disposition |
|---|---|---|---|
| 8 — `ai-queue-worker-every-minute` | Every minute | Inactive | Keep inactive; do not re-enable without a controlled auth test and approved need. |
| 10 — `founder-notification-daily-digest` | Daily | Inactive | Keep inactive while Founder-OS notification workflow is retired. |

### Deployed Edge Functions

The following were still reported ACTIVE during the same inspection; the job state does not turn these endpoints off:

| Function | Version | Required disposition before cloud retirement |
|---|---:|---|
| `api-v1` | 8 | Prove callers are absent or retire endpoint with an explicit response. |
| `create-checkout` | 8 | No current order data; confirm provider/caller configuration before retirement. |
| `payment-webhook` | 12 | Confirm external webhook is disabled at its provider, then retire. |
| `create-revenue-checkout` | 10 | No current revenue-order/opportunity data; retire after caller check. |
| `ai-execute` | 23 | CORE execution path; not replaced by the local CLI. Disable/retire after caller check. |
| `ai-queue-worker` | 20 | Scheduler is off; endpoint remains deployed and needs explicit retirement. |
| `revenue-order-transition` | 5 | No current revenue orders; retire after caller and trigger check. |
| `review-packet-decision` | 5 | Preserve decision/evidence only if required; otherwise export then retire. |
| `founder-notification-worker` | 5 | Daily schedule is off; retire after checking any direct callers. |
| `public-intake` | 7 | Previously described as an HTTP 410 tombstone; verify deployed response and absence of clients before removal. |

### Read-only data counts

Observed by read-only SQL inspection at `2026-10-14T21:56:18Z`: 54 applied migration-history rows; 16 configured AI-agent rows; 4 `ai_tasks` rows (1 each queued, completed, failed, and cancelled); 34,031 `ai_activity` rows; 1 Auth user; 0 Storage objects; 0 client-service inquiries; 0 revenue opportunities; 0 revenue orders; 0 API orders.

These are counts only. They do not include a row-by-row export, establish the business meaning of every activity record, or prove that no external caller exists.

### Secret and traffic handling

The owner reports disabling the Gemini key in Supabase CORE and deleting it from the CORE GitHub repository. That is not independently proof of provider-side revocation or of removal from every historical copy. Revoke/rotate at the provider if the credential may have been exposed. Never export secret values into this repository.

The most recent log query during this audit found no Gemini/provider-name matches in the aggregated hourly window, while the earlier window still contained 401 responses from the minute-level worker. Absence of a matching log string is not proof that all provider use is impossible. Both known cron jobs were inactive at the live read.

## What has actually migrated

- The human approval, evidence-level, and No Proof No Claim rules are now expressed in a PusingCuk-owned source document.
- The local-first provider separation, secret hygiene, bounded retries, registered-tool/capability rules, and explicit sandbox limitation are now expressed in a PusingCuk-owned source document.
- The conceptual 1,000-hectare masterplan, research-first principles, digital-phase gates, human-evidence transitions, and economic non-promise boundaries are distilled into `docs/knowledge/KAWASAN_MASJID_MASTERPLAN_AND_OPERATING_MODEL.md`.
- The active PusingCuk AI index will reference only the three new destination-owned documents; old repository indexes are not copied into runtime retrieval.
- Detailed Founder-OS raw memory, the entire CORE SQL/backend, payment handlers, and Supabase rows are not treated as model training data. They are excluded or slated for retirement, not represented as migrated implementation.

## GitHub repository deletion readiness

**READY for deleting the Founder-OS and CORE GitHub repositories from the selected-scope migration and PusingCuk dependency standpoint.** Verified state at PusingCuk HEAD `e54fc10668b0fe09d4bb315949438abbb7ad618f`:

- PusingCuk's active knowledge index has 20 records, all owned by `rllibo833-sudo/pusingcuk`; it does not load either external repository's knowledge index at runtime.
- Decision/evidence governance, local-model and registered-rule safety, conceptual masterplan/economic gates, and the transfer manifest have source-owned PusingCuk copies. Their external links are historical provenance, not runtime dependencies.
- The 20-case Indonesian retrieval regression and the Python/native/PVM suites passed; both PusingCuk CI workflows succeeded for this HEAD.
- Six non-essential CORE scheduled/manual workflows, including the manual Gemini review workflow and the scheduled Issue gateway, have been removed. CORE's remaining workflows are quality CI, manual/fail-closed Supabase deployment, and release.
- The unselected raw Founder-OS memory, complete CORE web/backend/payment system, and historical operational rows were deliberately excluded rather than falsely represented as migrated into the AI knowledge corpus.

The two source repositories themselves have **not** been deleted or archived. No Issue or Pull Request was opened. Deletion of source repositories is separate from permanent deletion of the Supabase database/project.

## Single Supabase database direction for PusingCuk

**Decision (2026-10-15): use the one existing project `lnpzgrodwnhthcwudebk` as the sole database project for the PusingCuk ecosystem; do not create a second project.** There is no second Supabase project to merge:

- Connection `Primary` points to the Free organization `Pusingcuk`; it currently has **zero projects**.
- Connection `Supabase` points to the Free organization `Kawasan-masjid-1000ha`; it contains the sole existing project `lnpzgrodwnhthcwudebk`.
- The database remains in the Kawasan organization for now. The available ChatGPT connector does not expose a project-transfer operation, and ownership transfer is not required merely to designate the existing project as the single intended database.
- No new project, schema, or table was created by this decision. Existing CORE tables and operational records are preserved, not represented as if already migrated to PusingCuk.
- **The PusingCuk runtime is not yet connected to this database.** That requires a specific application use case and a correctly scoped authentication/data-access path. Never put the database password or service-role key in the public repository, a distributable CLI, or browser JavaScript. Do not point PusingCuk directly at old CORE tables without reviewing schema ownership and access policies.
- Both organizations are on Free; this path avoids creating a new paid resource.

## Project restore and safety state

On 2026-10-15, a restore request for the sole existing project was accepted (`success: true`). The latest live status observed was `COMING_UP`, so it is **not yet confirmed `ACTIVE_HEALTHY`**. Wait until the provider reports healthy before any data/schema operations.

The two inspected cron jobs remain inactive. Ten Edge Functions were reported deployed and active before the project was paused; restoring the project may make those existing routes available again. Before exposing the database to PusingCuk, re-check those routes and their auth boundaries. No data or schema was deleted or rewritten.

A private database export and a successful restore rehearsal have not been produced. Do not permanently delete the only project: previous read-only counts are a snapshot, not a backup.

## Single Supabase database direction for PusingCuk

**Decision (2026-10-15): use the one existing project `lnpzgrodwnhthcwudebk` as the sole database project for the PusingCuk ecosystem; do not create a second project.** There is no second Supabase project to merge:

- Connection `Primary` points to the Free organization `Pusingcuk`; it currently has **zero projects**.
- Connection `Supabase` points to the Free organization `Kawasan-masjid-1000ha`; it contains the sole existing project `lnpzgrodwnhthcwudebk`.
- The database remains in the Kawasan organization for now. The available ChatGPT connector does not expose a project-transfer operation, and ownership transfer is not required merely to designate the existing project as the single intended database.
- No new project, schema, or table was created by this decision. Existing CORE tables and operational records are preserved, not represented as if already migrated to PusingCuk.
- **The PusingCuk runtime is not yet connected to this database.** That requires a specific application use case and a correctly scoped authentication/data-access path. Never put the database password or service-role key in the public repository, a distributable CLI, or browser JavaScript. Do not point PusingCuk directly at old CORE tables without reviewing schema ownership and access policies.
- Both organizations are on Free; this path avoids creating a new paid resource.

## Project restore and safety state

On 2026-10-15, a restore request for the sole existing project was accepted (`success: true`). The latest live status observed was `COMING_UP`, so it is **not yet confirmed `ACTIVE_HEALTHY`**. Wait until the provider reports healthy before any data/schema operations.

The two inspected cron jobs remain inactive. Ten Edge Functions were reported deployed and active before the project was paused; restoring the project may make those existing routes available again. Before exposing the database to PusingCuk, re-check those routes and their auth boundaries. No data or schema was deleted or rewritten.

A private database export and a successful restore rehearsal have not been produced. Do not permanently delete the only project: previous read-only counts are a snapshot, not a backup.

