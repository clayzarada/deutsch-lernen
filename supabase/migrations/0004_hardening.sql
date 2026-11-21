-- Security hardening from the review. Run once in the Supabase SQL editor. Safe to run again.

-- Only the signed-in user's own Plus status can be asked about (is_plus(any id) stays server-only).
create or replace function public.my_plus() returns boolean
language sql stable security definer set search_path = public as $$ select public.is_plus(auth.uid()) $$;
revoke all on function public.my_plus() from public, anon;
grant execute on function public.my_plus() to authenticated;
revoke execute on function public.is_plus(uuid) from authenticated;

-- Cloud backups: only the app's file names, and at most 10 per account (the app keeps 5).
drop policy if exists "backups: add own while Plus" on storage.objects;
create policy "backups: add own while Plus" on storage.objects for insert to authenticated
  with check (
    bucket_id = 'backups'
    and (storage.foldername(name))[1] = auth.uid()::text
    and name ~ ('^' || auth.uid()::text || '/[0-9]{8}-[0-9]{6}\.db\.gz$')
    and public.my_plus()
    and (select count(*) from storage.objects o
         where o.bucket_id = 'backups' and (storage.foldername(o.name))[1] = auth.uid()::text) < 10
  );

-- Survey answers and usage summaries: sensible sizes only.
alter table public.survey_answers drop constraint if exists sa_len;
alter table public.survey_answers add constraint sa_len check (
  char_length(coalesce(comment, '')) <= 2000 and char_length(install_id) <= 64
  and char_length(coalesce(answer, '')) <= 64 and char_length(coalesce(app_version, '')) <= 32);
alter table public.usage_summaries drop constraint if exists us_len;
alter table public.usage_summaries add constraint us_len check (
  char_length(install_id) <= 64 and char_length(coalesce(app_version, '')) <= 32
  and char_length(coalesce(ui_language, '')) <= 8 and char_length(coalesce(nav_layout, '')) <= 8
  and days_active between 0 and 7 and minutes between 0 and 10080);
