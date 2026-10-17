-- Tighten message RLS after adding project/conversation ownership checks.
-- Older user_id-only policies are permissive and would otherwise OR with the stricter policy.
drop policy if exists "Users insert own PusingCuk SaaS messages" on public.pusingcuk_saas_messages;
drop policy if exists "Users read own PusingCuk SaaS messages" on public.pusingcuk_saas_messages;
