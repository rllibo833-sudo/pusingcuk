-- PusingCuk v1 cloud feature: explicitly saved project notes per authenticated user.
-- No chat history or local SQLite records are synced by this schema.
create or replace function public.pusingcuk_set_project_notes_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := pg_catalog.now();
  return new;
end;
$$;

revoke all on function public.pusingcuk_set_project_notes_updated_at() from public, anon, authenticated, service_role;

create table if not exists public.pusingcuk_project_notes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null check (char_length(title) between 1 and 160 and title = btrim(title)),
  body text not null check (char_length(body) between 1 and 20000),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists pusingcuk_project_notes_user_updated_idx
  on public.pusingcuk_project_notes (user_id, updated_at desc);

drop trigger if exists pusingcuk_project_notes_touch_updated_at on public.pusingcuk_project_notes;
create trigger pusingcuk_project_notes_touch_updated_at
before update on public.pusingcuk_project_notes
for each row execute function public.pusingcuk_set_project_notes_updated_at();

alter table public.pusingcuk_project_notes enable row level security;
alter table public.pusingcuk_project_notes force row level security;

drop policy if exists pusingcuk_notes_select_own on public.pusingcuk_project_notes;
create policy pusingcuk_notes_select_own
on public.pusingcuk_project_notes for select to authenticated
using ((select auth.uid()) is not null and user_id = (select auth.uid()));

drop policy if exists pusingcuk_notes_insert_own on public.pusingcuk_project_notes;
create policy pusingcuk_notes_insert_own
on public.pusingcuk_project_notes for insert to authenticated
with check ((select auth.uid()) is not null and user_id = (select auth.uid()));

drop policy if exists pusingcuk_notes_update_own on public.pusingcuk_project_notes;
create policy pusingcuk_notes_update_own
on public.pusingcuk_project_notes for update to authenticated
using ((select auth.uid()) is not null and user_id = (select auth.uid()))
with check ((select auth.uid()) is not null and user_id = (select auth.uid()));

drop policy if exists pusingcuk_notes_delete_own on public.pusingcuk_project_notes;
create policy pusingcuk_notes_delete_own
on public.pusingcuk_project_notes for delete to authenticated
using ((select auth.uid()) is not null and user_id = (select auth.uid()));

revoke all on table public.pusingcuk_project_notes from public, anon, authenticated, service_role;
grant select, insert, update, delete on table public.pusingcuk_project_notes to authenticated;
