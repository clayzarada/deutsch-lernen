-- Deutsch lernen Plus: accounts, subscription status and AI usage.
-- Run once in the Supabase SQL editor. Safe to run again.

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text,
  plan text not null default 'free' check (plan in ('free', 'plus')),
  plus_until timestamptz,                 -- Plus is active while now() < plus_until (null = no end date)
  ai_cap_usd numeric(8, 2),               -- per-account override of the monthly AI limit (null = default)
  paddle_customer_id text,
  paddle_subscription_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.ai_usage (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  feature text,
  model text,
  input_tokens integer not null default 0,
  output_tokens integer not null default 0,
  cache_read integer not null default 0,
  cache_write integer not null default 0,
  web_searches integer not null default 0,
  cost_usd numeric(10, 6) not null default 0
);
create index if not exists ai_usage_user_month on public.ai_usage (user_id, created_at);

-- Users may read their own rows. Nobody writes from the app: only the server function (service role) does.
alter table public.profiles enable row level security;
alter table public.ai_usage enable row level security;
drop policy if exists "read own profile" on public.profiles;
create policy "read own profile" on public.profiles for select using (auth.uid() = user_id);
drop policy if exists "read own usage" on public.ai_usage;
create policy "read own usage" on public.ai_usage for select using (auth.uid() = user_id);

-- A profile row for every new account.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (user_id, email) values (new.id, new.email) on conflict (user_id) do nothing;
  return new;
end $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- Accounts made before this script ran.
insert into public.profiles (user_id, email) select id, email from auth.users on conflict (user_id) do nothing;

-- Delete account: the signed-in user removes themself (profile and usage go with it via cascade).
create or replace function public.delete_my_account() returns void
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  delete from auth.users where id = auth.uid();
end $$;
revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;
