-- In-app questions and weekly usage summaries.
-- Add a question by inserting a row into public.surveys (see the example at the bottom); the app shows a small (!)
-- in the sidebar until the learner answers or skips it. Answers are linked to the account when the learner is
-- signed in, and always to the install id, so they can be compared with the weekly usage numbers.
-- Run once in the Supabase SQL editor. Safe to run again.

create table if not exists public.surveys (
  id text primary key,                         -- short name, e.g. 'nav-layout-2026-11'
  title text not null,                          -- the (!) link's text, e.g. 'Quick question'
  question text not null,
  kind text not null check (kind in ('choice', 'image_choice', 'rating', 'text')),
  options jsonb not null default '[]',          -- [{"id": "a", "label": "...", "image": "https://..."}]
  allow_comment boolean not null default true,
  active boolean not null default true,
  starts_at timestamptz not null default now(),
  ends_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.survey_answers (
  id bigint generated always as identity primary key,
  survey_id text not null references public.surveys(id) on delete cascade,
  install_id text not null,
  user_id uuid references auth.users(id) on delete set null,
  answer text,                                  -- option id, rating 1-5, or null when skipped
  comment text,
  skipped boolean not null default false,
  app_version text,
  created_at timestamptz not null default now(),
  unique (survey_id, install_id)
);

create table if not exists public.usage_summaries (
  id bigint generated always as identity primary key,
  install_id text not null,
  user_id uuid references auth.users(id) on delete set null,
  week date not null,                           -- the Monday the week starts on
  days_active integer not null default 0,
  minutes integer not null default 0,
  cards_reviewed integer not null default 0,
  answers integer not null default 0,
  lessons_done integer not null default 0,
  total_cards integer not null default 0,
  first_use date,
  app_version text,
  ui_language text,
  nav_layout text,
  has_own_key boolean,
  created_at timestamptz not null default now(),
  unique (install_id, week)
);

alter table public.surveys enable row level security;
alter table public.survey_answers enable row level security;
alter table public.usage_summaries enable row level security;

-- Anyone running the app can read the current questions.
drop policy if exists "surveys: read open" on public.surveys;
create policy "surveys: read open" on public.surveys for select to anon, authenticated
  using (active and starts_at <= now() and (ends_at is null or ends_at > now()));

-- Anyone can add answers and summaries, but only for themselves: an account id must be their own (or empty).
-- Nobody can read them back from the app; you read them in the dashboard.
drop policy if exists "answers: add own" on public.survey_answers;
create policy "answers: add own" on public.survey_answers for insert to anon, authenticated
  with check (user_id is null or user_id = auth.uid());
drop policy if exists "usage: add own" on public.usage_summaries;
create policy "usage: add own" on public.usage_summaries for insert to anon, authenticated
  with check (user_id is null or user_id = auth.uid());

grant select on public.surveys to anon, authenticated;
grant insert on public.survey_answers, public.usage_summaries to anon, authenticated;

-- One row per answer with what's known about the learner: account age and plan (if signed in) and their latest
-- weekly usage. Open it in the Table Editor, or run:  select * from public.survey_results where survey_id = '...';
create or replace view public.survey_results with (security_invoker = true) as
select a.survey_id, a.answer, a.skipped, a.comment, a.created_at as answered_at, a.app_version,
       a.user_id, p.email, p.plan, (now()::date - u.created_at::date) as account_age_days,
       s.week as usage_week, s.days_active, s.minutes, s.cards_reviewed, s.answers as exercises_answered,
       s.lessons_done, s.total_cards, s.first_use, (now()::date - s.first_use) as days_since_first_use,
       s.ui_language, s.nav_layout, s.has_own_key, a.install_id
from public.survey_answers a
left join public.profiles p on p.user_id = a.user_id
left join auth.users u on u.id = a.user_id
left join lateral (select * from public.usage_summaries s where s.install_id = a.install_id
                   order by s.week desc limit 1) s on true;
revoke all on public.survey_results from anon, authenticated;

-- Example: the first question. "try" makes the app switch to that layout behind the dialog when it's picked,
-- so people compare the real thing. (For pictures instead, use kind 'image_choice' and an "image" URL per option.)
insert into public.surveys (id, title, question, kind, options)
values ('nav-layout-2026-11', 'Quick question',
        'Which layout do you like better? You can switch any time in Settings; this just helps decide the default.',
        'choice',
        '[{"id": "side", "label": "Pages listed under each section in the sidebar", "try": "nav:side"},
          {"id": "top", "label": "Pages as tabs across the top", "try": "nav:top"}]')
on conflict (id) do nothing;
