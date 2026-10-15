# Supabase project map for PusingCuk

**Last verified:** 2026-10-15  
**Status:** schema applied and SQL RLS smoke passed; application integration not yet implemented.

## Project assignments

| Use | Supabase project ref | Project URL | State |
|---|---|---|---|
| PusingCuk project notes (schema applied) | `vcvejjpzklpvknxmymgy` | `https://vcvejjpzklpvknxmymgy.supabase.co` | Active/healthy; versioned notes table with RLS, SQL access smoke passed; runtime not connected |
| Legacy Kawasan Masjid / CORE data | `lnpzgrodwnhthcwudebk` | `https://lnpzgrodwnhthcwudebk.supabase.co` | Active/healthy; existing schema/data; do not use as the default target for new PusingCuk writes |

Both projects currently sit in the Free organization `Kawasan-masjid-1000ha`. That is an acceptable arrangement: different Supabase project refs represent separate project/database instances. The separate organization named `Pusingcuk` does not currently need a project for these two projects to remain isolated. Do not create or transfer projects just to make the organization labels look different.

## What is connected today?

Nothing in the PusingCuk runtime is configured to use this Supabase project yet. In the current repository, `library/adapters/database.py` is an offline-first, confined SQLite adapter. Selecting a project and knowing its API URL do not connect that adapter to Postgres or make cloud persistence available.

This is intentional until a specific application data use-case and access model are agreed upon. Do not claim users, sessions, AI memories, language-runtime files, or local SQLite data are synchronized to Supabase.

## First cloud use case: private project notes

Selected use case: a signed-in user explicitly saves project notes and can retrieve them from another device. This does **not** mirror chat history or the local SQLite database. The versioned schema is `supabase/migrations/20261015002334_pusingcuk_project_notes_v1.sql`. Each note references `auth.users`; RLS is enabled and forced, and separate select/insert/update/delete policies limit access to `auth.uid()`. Table privileges are revoked from `anon`, `public`, and `service_role`; only `authenticated` receives row-operation grants.

The rollback smoke script is `supabase/tests/20261015002334_pusingcuk_project_notes_smoke.sql`. The external EXECUTE grants on the existing project-level `public.rls_auto_enable()` event-trigger function were also revoked by `supabase/migrations/20261015002509_restrict_public_rls_auto_enable_execution.sql`; the event trigger remains active and a temporary-table probe confirmed it still enables RLS. It simulates two authenticated identities and checks owner CRUD, spoofed insert denial, cross-user invisibility and blocked update/delete. This SQL role-level test is not a REST API or application-runtime integration test. Never publish privileged keys; this schema does not require a service-role key for end-user CRUD.

**Database smoke status (2026-10-15):** migration version `20261015002334` was applied to `vcvejjpzklpvknxmymgy`. A live SQL transaction test passed owner insert/read/update, denied cross-user insert, hid owner rows from another user, denied cross-user update/delete, confirmed no `anon` table grant, and rolled back all test data. A temporary table probe also confirmed the project-level `ensure_rls` event trigger still enables RLS after its function's external EXECUTE grants were revoked. Supabase security and performance advisors returned zero lints after that change. **Application status:** still not connected; this does not prove REST/Auth integration from PusingCuk's runtime.

## Safe integration checklist for the next feature

1. Define the records and operations the feature needs; do not mirror the legacy CORE schema by default.
2. Add a versioned migration under a clearly documented Supabase migration directory and test it against this dedicated PusingCuk project.
3. Decide whether access is anonymous, authenticated-user scoped, or server-only. Enable row-level security for exposed tables and write policies for that exact model.
4. Use only a publishable key in browser code, and only with suitable authentication and RLS. Keep service-role/secret keys and database passwords on a trusted server or encrypted secret store—never in the public repository, browser JavaScript, app package, or logs.
5. Run a least-privilege smoke test and security advisor checks before calling the integration ready.
6. Keep the legacy Kawasan/CORE project unchanged until a private backup and restore rehearsal exist and every external caller has been accounted for.

## Current limitations

- The project now has one application table (`pusingcuk_project_notes`) with owner-scoped RLS. No PusingCuk runtime/API adapter uses the table yet.
- No database dump or restore rehearsal has been produced for the legacy project.
- Existing CORE scheduled jobs were previously found inactive, but that does not prove old Edge Function endpoints have no callers.
- Editing this document did not mutate the database. The only PusingCuk schema change is the versioned migration listed above; the SQL smoke transaction was rolled back.
