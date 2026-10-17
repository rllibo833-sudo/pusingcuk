# PusingCuk AI SaaS MVP

Status: **deployment candidate; verify live URL, auth, persistence, and provider before calling it production-ready**. This folder adds a responsive browser workspace and a small account/chat API that calls the existing `PusingCukAssistant`, knowledge index, and registered `ToolRegistry`. It does not introduce a second AI engine.

## What's in this MVP

- Responsive Indonesian web workspace for desktop and mobile.
- Email + password registration/login, hashed passwords (PBKDF2-HMAC-SHA256), opaque server-side sessions, HttpOnly/SameSite cookie.
- Supabase Auth for account registration/login and Supabase Postgres + RLS for durable chat transcripts. No service-role key is used by the application.
- Origin check on every POST, bounded JSON payloads, generic provider errors, and simple per-process rate limits.
- Existing provider adapters only: Ollama (loopback-only) or the repository's existing optional Gemini adapter. Gemini is a provider choice, not a new assistant/engine.

## Run locally

From the repository root:

```sh
export PUSINGCUK_SAAS_PUBLIC_ORIGIN=http://127.0.0.1:8088
export PUSINGCUK_SAAS_COOKIE_SECURE=0
export PUSINGCUK_SAAS_DB=/tmp/pusingcuk-saas-dev.sqlite3
export PUSINGCUK_AI_PROVIDER=ollama
export PUSINGCUK_AI_MODEL=qwen3:4b
python apps/pusingcuk-ai-saas/server.py
```

Ollama and the selected model must already be running on the same host. Open `http://127.0.0.1:8088`. Use only test data for local development.

For Render, use repository root as Docker context and `apps/pusingcuk-ai-saas/Dockerfile` as Dockerfile. Configure `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `PUSINGCUK_SAAS_PUBLIC_ORIGIN` (exact HTTPS origin), `PUSINGCUK_AI_PROVIDER=gemini`, and `GEMINI_API_KEY`. The service listens on Render's `PORT` and relies on Render's HTTPS edge.

## Required production work before accepting real users

This is an MVP foundation, not a production SaaS launch. Before launch, add and verify: email verification and password reset, account deletion/export, privacy/retention controls, cross-process rate limiting, durable conversation restoration, bounded/locked per-user inference scheduling, CSRF and deployment-origin integration tests, dependency and security scans, monitoring, backups/restore tests, abuse controls, billing/quotas if monetized, and an independently reviewed deployment boundary. The SQLite file must live on persistent storage and must not be committed. Never execute arbitrary model-generated source in the server process; the existing compiler check is not a sandbox.

## Honest capability boundaries

- A successful AI answer is not proof that a generated program runs.
- The existing `cuk_compile_check` only reports its documented compilation evidence; it is not a general runtime sandbox.
- This UI is a first working product surface, not a published service. No public URL, cloud deployment, provider availability, or production security review is claimed by this commit.
