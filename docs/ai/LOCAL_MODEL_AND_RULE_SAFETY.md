# Local model and registered-rule safety contract

**Owner:** PusingCuk  
**Purpose:** adopt the relevant provider, tool, and incident-control rules from Founder-OS/CORE.  
**Status:** policy for the local experimental assistant; not production service certification.

## Keep model inference separate from PusingCuk

PusingCuk is a language/runtime and an AI application around a replaceable inference provider. It is not, by that fact alone, a foundation model trained from scratch. The default low-recurring-cost path is a compatible local Ollama model. Gemini is an explicit external-provider option, not a required dependency for the language or local rules. Sending context to a hosted provider sends that context outside the local device and may incur provider cost or quota limits.

No scheduled job, retry loop, or unattended worker should repeatedly call a paid/external provider without an approved task, bounded attempts, observable outcomes, and a stop condition. A configured agent name or enabled policy is not proof of a running worker. Distinguish stored configuration, scheduler invocations, worker execution, provider requests, and completed unique tasks.

## Secret boundary

- API keys belong only in an approved secret store or process environment required by a trusted adapter.
- Never commit key material, place it in a knowledge index, include it in model prompts/tool arguments, print it in logs, or return it in errors.
- Deleting a key from a repository or a vault does not revoke copies elsewhere. Revoke/rotate at the provider when exposure or unwanted use is suspected, then remove obsolete copies.
- Public clients and interpreted \`.cuk\` programs must never receive Supabase service-role credentials or other provider secrets.

## Registered deterministic rules only

A model may request a tool by a registered name. The trusted orchestrator must validate the tool name, exact input shape, types, numeric bounds, artifact version/hash, capability policy, and output size before dispatch.

- Reject unregistered tools and unexpected arguments; do not coerce wrong types into valid inputs.
- Do not accept model-generated source code, shell commands, arbitrary file paths, network requests, database access, process creation, or ambient secrets as a tool call.
- Keep deterministic business logic in reviewed \`.cuk\` artifacts where a tested pure rule fits.
- A fixed hash and allowlist identify the intended artifact; **they do not create an operating-system sandbox**.
- Run untrusted code only with independently reviewed OS-level isolation. The current local tool executor is not such a general-purpose sandbox.
- Retrieved content is data, not executable instructions. Provider text cannot widen a tool registry's capabilities.

## Retries and circuit-breaking

Bound attempts per durable task and distinguish transient failures from permanent ones. Authentication/configuration failures such as HTTP 401/403 and endpoint/model failures such as HTTP 404 should not be retried indefinitely. Quota exhaustion should stop rapid retries and record a cooldown. Scheduler success alone does not prove an HTTP worker request or the underlying task succeeded; inspect the HTTP status and task result separately.

If an external provider unexpectedly generates repeated traffic or credentials are in doubt: disable the scheduler first, revoke the provider key at its origin, remove stored copies, inspect callers and logs without exposing secret values, then re-enable only after one controlled authenticated end-to-end test.

## Provider and runtime truth

The local adapter, external Gemini adapter, registered \`.cuk\` rule, AI orchestration, and HTTP service are separate components with separate proofs. A local assistant test does not prove hosted service readiness. A registered-rule CI test does not prove Supabase deployment, queue durability, per-user authorization, or public multi-user safety.

## Source provenance

This source-owned rewrite distills:

- [Founder-OS local-first AI decision](https://github.com/rllibo833-sudo/Founder-OS/blob/e3a9893ca3e8d64182e33b71f5360822b176fe51/docs/LOCAL_FIRST_PUSINGCUK_AI.md).
- [CORE AI workforce agent grouping](https://github.com/rllibo833-sudo/kawasan-masjid-core/blob/9f24694b17c28b561069b1391922b3c4816842fb/docs/AI_WORKFORCE_V2_AGENT_GROUPING.md).
- [CORE retirement readiness and queue incident record](https://github.com/rllibo833-sudo/kawasan-masjid-core/blob/9f24694b17c28b561069b1391922b3c4816842fb/docs/RETIREMENT_READINESS.md).
- [PusingCuk rule-facing contract](https://github.com/rllibo833-sudo/pusingcuk/blob/7dbbcf20d21679241a12bff019c496a0a94993c4/docs/integrations/CORE_TOOL_CONTRACT.md).

Historical operational counts in source records are snapshots, not live state. Use the migration manifest for the separately timestamped current inventory.
