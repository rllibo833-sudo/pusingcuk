# Supabase project map for PusingCuk

**Last verified:** 2026-10-15  
**Status:** project selected; application integration not yet implemented.

## Project assignments

| Use | Supabase project ref | Project URL | State |
|---|---|---|---|
| Future PusingCuk-owned data | `vcvejjpzklpvknxmymgy` | `https://vcvejjpzklpvknxmymgy.supabase.co` | Active/healthy; no application tables, recorded migrations, or Edge Functions |
| Legacy Kawasan Masjid / CORE data | `lnpzgrodwnhthcwudebk` | `https://lnpzgrodwnhthcwudebk.supabase.co` | Active/healthy; existing schema/data; do not use as the default target for new PusingCuk writes |

Both projects currently sit in the Free organization `Kawasan-masjid-1000ha`. That is an acceptable arrangement: different Supabase project refs represent separate project/database instances. The separate organization named `Pusingcuk` does not currently need a project for these two projects to remain isolated. Do not create or transfer projects just to make the organization labels look different.

## What is connected today?

Nothing in the PusingCuk runtime is configured to use this Supabase project yet. In the current repository, `library/adapters/database.py` is an offline-first, confined SQLite adapter. Selecting a project and knowing its API URL do not connect that adapter to Postgres or make cloud persistence available.

This is intentional until a specific application data use-case and access model are agreed upon. Do not claim users, sessions, AI memories, language-runtime files, or local SQLite data are synchronized to Supabase.

## Safe integration checklist for a future feature

1. Define the records and operations the feature needs; do not mirror the legacy CORE schema by default.
2. Add a versioned migration under a clearly documented Supabase migration directory and test it against this dedicated PusingCuk project.
3. Decide whether access is anonymous, authenticated-user scoped, or server-only. Enable row-level security for exposed tables and write policies for that exact model.
4. Use only a publishable key in browser code, and only with suitable authentication and RLS. Keep service-role/secret keys and database passwords on a trusted server or encrypted secret store—never in the public repository, browser JavaScript, app package, or logs.
5. Run a least-privilege smoke test and security advisor checks before calling the integration ready.
6. Keep the legacy Kawasan/CORE project unchanged until a private backup and restore rehearsal exist and every external caller has been accounted for.

## Current limitations

- The project has no application tables, recorded migration history, or Edge Functions as of the last inspection.
- No database dump or restore rehearsal has been produced for the legacy project.
- Existing CORE scheduled jobs were previously found inactive, but that does not prove old Edge Function endpoints have no callers.
- No schema or data was changed by writing this document.
