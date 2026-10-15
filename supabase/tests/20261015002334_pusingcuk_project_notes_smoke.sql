-- Manual live database smoke test. Execute as database owner against a disposable/empty
-- PusingCuk project only after the versioned migration has been applied.
-- The whole transaction is rolled back. These checks simulate Auth claims and the
-- authenticated Postgres role; they are not an end-to-end client/REST API test.
begin;

insert into auth.users
  (id, instance_id, aud, role, email, encrypted_password, email_confirmed_at,
   raw_app_meta_data, raw_user_meta_data, created_at, updated_at)
values
  ('10000000-0000-4000-8000-000000000001','00000000-0000-0000-0000-000000000000',
   'authenticated','authenticated','pc-smoke-a@example.invalid','',now(),
   '{"provider":"email","providers":["email"]}','{}',now(),now()),
  ('10000000-0000-4000-8000-000000000002','00000000-0000-0000-0000-000000000000',
   'authenticated','authenticated','pc-smoke-b@example.invalid','',now(),
   '{"provider":"email","providers":["email"]}','{}',now(),now())
on conflict (id) do nothing;

do $$
declare table_rls boolean; table_force_rls boolean; policy_total integer;
begin
  select c.relrowsecurity, c.relforcerowsecurity into table_rls, table_force_rls
  from pg_class c join pg_namespace n on n.oid=c.relnamespace
  where n.nspname='public' and c.relname='pusingcuk_project_notes';
  if table_rls is not true or table_force_rls is not true then raise exception 'RLS_NOT_ENABLED_OR_FORCED'; end if;
  select count(*) into policy_total from pg_policies where schemaname='public'
    and tablename='pusingcuk_project_notes'
    and policyname in ('pusingcuk_notes_select_own','pusingcuk_notes_insert_own','pusingcuk_notes_update_own','pusingcuk_notes_delete_own');
  if policy_total <> 4 then raise exception 'RLS_POLICY_SET_INVALID'; end if;
  if has_table_privilege('anon','public.pusingcuk_project_notes','select') then raise exception 'ANON_HAS_TABLE_ACCESS'; end if;
  if not has_table_privilege('authenticated','public.pusingcuk_project_notes','select') then raise exception 'AUTHENTICATED_ACCESS_MISSING'; end if;
end $$;

set local role authenticated;
select set_config('request.jwt.claim.role','authenticated',true);
select set_config('request.jwt.claim.sub','10000000-0000-4000-8000-000000000001',true);

insert into public.pusingcuk_project_notes(user_id,title,body)
values ('10000000-0000-4000-8000-000000000001','smoke-a','note from user A');

do $$
declare n integer;
begin
  select count(*) into n from public.pusingcuk_project_notes where title='smoke-a';
  if n <> 1 then raise exception 'RLS_OWNER_READ_FAILED'; end if;
  begin
    insert into public.pusingcuk_project_notes(user_id,title,body)
    values ('10000000-0000-4000-8000-000000000002','spoofed','must be denied');
    raise exception 'RLS_CROSS_USER_INSERT_ALLOWED';
  exception when insufficient_privilege then
    null;
  end;
end $$;

update public.pusingcuk_project_notes set body='updated by owner'
where title='smoke-a';
do $$
declare n integer; body_value text;
begin
  select count(*), max(body) into n, body_value from public.pusingcuk_project_notes where title='smoke-a';
  if n <> 1 or body_value <> 'updated by owner' then raise exception 'RLS_OWNER_UPDATE_FAILED'; end if;
end $$;

select set_config('request.jwt.claim.sub','10000000-0000-4000-8000-000000000002',true);
do $$
declare n integer; affected integer;
begin
  select count(*) into n from public.pusingcuk_project_notes where title='smoke-a';
  if n <> 0 then raise exception 'RLS_CROSS_USER_READ_LEAK'; end if;
  update public.pusingcuk_project_notes set body='cross-user update' where title='smoke-a';
  get diagnostics affected = row_count;
  if affected <> 0 then raise exception 'RLS_CROSS_USER_UPDATE_ALLOWED'; end if;
  delete from public.pusingcuk_project_notes where title='smoke-a';
  get diagnostics affected = row_count;
  if affected <> 0 then raise exception 'RLS_CROSS_USER_DELETE_ALLOWED'; end if;
end $$;

reset role;
rollback;
