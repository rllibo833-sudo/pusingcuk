-- Restrict the project-level auto-RLS event-trigger helper from API execution.
-- This remains registered as the DDL event trigger "ensure_rls"; only user-callable EXECUTE grants are removed.
do $$
begin
  if to_regprocedure('public.rls_auto_enable()') is not null then
    execute 'revoke all on function public.rls_auto_enable() from public, anon, authenticated, service_role';
  end if;
end
$$;
