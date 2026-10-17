-- PusingCuk AI SaaS workspace foundation
-- Adds per-user projects, project files, conversations, and links messages to them.
create table if not exists public.pusingcuk_saas_projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 120 and name = btrim(name)),
  description text not null default '' check (char_length(description) <= 2000),
  status text not null default 'active' check (status in ('active','archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.pusingcuk_saas_project_files (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.pusingcuk_saas_projects(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  path text not null check (char_length(path) between 1 and 240 and path = btrim(path)),
  content text not null default '' check (char_length(content) <= 200000),
  language text not null default 'text' check (char_length(language) <= 40),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (project_id, path)
);
create table if not exists public.pusingcuk_saas_conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  project_id uuid references public.pusingcuk_saas_projects(id) on delete cascade,
  title text not null default 'Percakapan baru' check (char_length(title) between 1 and 160),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.pusingcuk_saas_messages add column if not exists project_id uuid references public.pusingcuk_saas_projects(id) on delete cascade;
alter table public.pusingcuk_saas_messages add column if not exists conversation_id uuid references public.pusingcuk_saas_conversations(id) on delete cascade;
create index if not exists pusingcuk_saas_projects_user_updated_idx on public.pusingcuk_saas_projects(user_id, updated_at desc);
create index if not exists pusingcuk_saas_project_files_project_idx on public.pusingcuk_saas_project_files(project_id, path);
create index if not exists pusingcuk_saas_conversations_user_updated_idx on public.pusingcuk_saas_conversations(user_id, updated_at desc);
create index if not exists pusingcuk_saas_messages_conversation_created_idx on public.pusingcuk_saas_messages(conversation_id, created_at);
alter table public.pusingcuk_saas_projects enable row level security;
alter table public.pusingcuk_saas_project_files enable row level security;
alter table public.pusingcuk_saas_conversations enable row level security;
drop policy if exists "Users manage own PusingCuk projects" on public.pusingcuk_saas_projects;
create policy "Users manage own PusingCuk projects" on public.pusingcuk_saas_projects for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists "Users manage own PusingCuk project files" on public.pusingcuk_saas_project_files;
create policy "Users manage own PusingCuk project files" on public.pusingcuk_saas_project_files for all using (auth.uid() = user_id and exists (select 1 from public.pusingcuk_saas_projects p where p.id = project_id and p.user_id = auth.uid())) with check (auth.uid() = user_id and exists (select 1 from public.pusingcuk_saas_projects p where p.id = project_id and p.user_id = auth.uid()));
drop policy if exists "Users manage own PusingCuk conversations" on public.pusingcuk_saas_conversations;
create policy "Users manage own PusingCuk conversations" on public.pusingcuk_saas_conversations for all using (auth.uid() = user_id) with check (auth.uid() = user_id and (project_id is null or exists (select 1 from public.pusingcuk_saas_projects p where p.id = project_id and p.user_id = auth.uid())));
drop policy if exists "Users manage own PusingCuk messages" on public.pusingcuk_saas_messages;
create policy "Users manage own PusingCuk messages" on public.pusingcuk_saas_messages for all using (auth.uid() = user_id) with check (auth.uid() = user_id and (project_id is null or exists (select 1 from public.pusingcuk_saas_projects p where p.id = project_id and p.user_id = auth.uid())) and (conversation_id is null or exists (select 1 from public.pusingcuk_saas_conversations c where c.id = conversation_id and c.user_id = auth.uid())));
create or replace function public.pusingcuk_touch_updated_at() returns trigger language plpgsql as $$ begin new.updated_at = now(); return new; end; $$;
drop trigger if exists pusingcuk_projects_touch_updated_at on public.pusingcuk_saas_projects;
create trigger pusingcuk_projects_touch_updated_at before update on public.pusingcuk_saas_projects for each row execute function public.pusingcuk_touch_updated_at();
drop trigger if exists pusingcuk_project_files_touch_updated_at on public.pusingcuk_saas_project_files;
create trigger pusingcuk_project_files_touch_updated_at before update on public.pusingcuk_saas_project_files for each row execute function public.pusingcuk_touch_updated_at();
drop trigger if exists pusingcuk_conversations_touch_updated_at on public.pusingcuk_saas_conversations;
create trigger pusingcuk_conversations_touch_updated_at before update on public.pusingcuk_saas_conversations for each row execute function public.pusingcuk_touch_updated_at();
