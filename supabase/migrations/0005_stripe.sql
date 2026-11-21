-- Deutsch lernen Plus: payments through Stripe (Stripe Managed Payments) next to the older Paddle setup.
-- Run once in the Supabase SQL editor BEFORE deploying the billing, stripe and updated paddle functions. Safe to run again.

-- The Stripe side of a subscription. The Paddle columns stay: existing subscriptions may still use them.
alter table public.profiles add column if not exists stripe_customer_id text;
alter table public.profiles add column if not exists stripe_subscription_id text;
alter table public.profiles add column if not exists stripe_status text;   -- Stripe's status: active, past_due, canceled...
-- Which provider granted the current Plus. A webhook only ends Plus that its own provider granted, so someone who
-- moved from Paddle to Stripe (or back) isn't cut off when the old subscription runs out.
alter table public.profiles add column if not exists plus_source text;
alter table public.profiles drop constraint if exists profiles_plus_source;
alter table public.profiles add constraint profiles_plus_source check (plus_source is null or plus_source in ('paddle', 'stripe'));
update public.profiles set plus_source = 'paddle'
  where plus_source is null and plan = 'plus' and paddle_subscription_id is not null;

-- The webhook finds the account by these.
create index if not exists profiles_stripe_customer on public.profiles (stripe_customer_id);
create index if not exists profiles_stripe_subscription on public.profiles (stripe_subscription_id);

-- Plus itself doesn't depend on the provider: both webhooks write plan and plus_until, and these read only those.
-- Restated here unchanged so this file shows the whole rule in one place.
create or replace function public.is_plus(uid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles p
                 where p.user_id = uid and p.plan = 'plus' and (p.plus_until is null or p.plus_until > now()));
$$;
revoke all on function public.is_plus(uuid) from public, anon, authenticated;

create or replace function public.my_plus() returns boolean
language sql stable security definer set search_path = public as $$ select public.is_plus(auth.uid()) $$;
revoke all on function public.my_plus() from public, anon;
grant execute on function public.my_plus() to authenticated;
