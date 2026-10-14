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

Observed by read-only SQL inspection: 16 configured AI-agent rows; 4 `ai_tasks` rows (1 each queued, completed, failed, and cancelled); 34,031 `ai_activity` rows; 1 Auth user; 0 Storage objects; 0 client-service inquiries; 0 revenue opportunities; 0 revenue orders; 0 API orders.

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

## Remaining exit gate

**The selected knowledge migration is complete; repository/cloud deletion readiness is not yet proven.** Before deleting the source repositories or pausing/deleting the Supabase project, record the following operational outcomes:

1. Export the required Supabase schema and data using an approved private backup path; exclude secrets and do not commit user/operational records to this public repository.
2. Restore that export to a separate environment and validate required relationships and counts.
3. Confirm and explicitly retire all ten deployed Edge Functions and any direct callers/webhooks; both cron jobs already being inactive does not retire those functions.
4. Reconcile the live database migration-history/source discrepancy documented by CORE; do not force-mark migrations applied to make counts match.
5. Verify there are no GitHub workflows, other repositories, webhooks, or operator runbooks that must deploy or fetch CORE/Founder-OS.
6. Retain this transfer manifest and the immutable source SHAs, then complete the owner's deletion decision.

No repository, table, user, secret, Edge Function, or Supabase project was deleted by this migration.


## Follow-on changes after the initial live snapshot

- The six non-essential scheduled/manual CORE automation workflows and the manual Gemini assistant workflow were removed from CORE `main` in commit [`4cc9a04fbedb6540f227c2cae84def26abc5b19d`](https://github.com/rllibo833-sudo/kawasan-masjid-core/commit/4cc9a04fbedb6540f227c2cae84def26abc5b19d). CORE retains only quality CI, manual/fail-closed Supabase deployment, and release workflow. A follow-up commit aligns the stale static queue-auth assertion with the implementation's configured-secret set.
- A reversible Supabase pause request was accepted for project `lnpzgrodwnhthcwudebk`; the last successful project status observed immediately after the request was `PAUSING`. A final `PAUSED` state could not be re-read through the connected tool after the transition started. Treat production pause as requested, not verified complete.
- The selected transfer is not yet a verified complete repository-deletion gate: a private database export and separate-environment restore rehearsal have not been produced or proven by this work.
