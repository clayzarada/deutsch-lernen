-- Deutsch lernen Plus: cloud backups of the study database.
-- Each account has a folder named after its id in the private "backups" bucket. Only Plus accounts can add backups;
-- anyone can still list, download and delete their own (so a backup made during Plus can be restored later).
-- Run once in the Supabase SQL editor. Safe to run again.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('backups', 'backups', false, 52428800, array['application/gzip'])
on conflict (id) do update set public = false, file_size_limit = 52428800, allowed_mime_types = array['application/gzip'];

create or replace function public.is_plus(uid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles p
                 where p.user_id = uid and p.plan = 'plus' and (p.plus_until is null or p.plus_until > now()));
$$;
revoke all on function public.is_plus(uuid) from public, anon;
grant execute on function public.is_plus(uuid) to authenticated;

drop policy if exists "backups: read own" on storage.objects;
create policy "backups: read own" on storage.objects for select to authenticated
  using (bucket_id = 'backups' and (storage.foldername(name))[1] = auth.uid()::text);

drop policy if exists "backups: add own while Plus" on storage.objects;
create policy "backups: add own while Plus" on storage.objects for insert to authenticated
  with check (bucket_id = 'backups' and (storage.foldername(name))[1] = auth.uid()::text and public.is_plus(auth.uid()));

drop policy if exists "backups: delete own" on storage.objects;
create policy "backups: delete own" on storage.objects for delete to authenticated
  using (bucket_id = 'backups' and (storage.foldername(name))[1] = auth.uid()::text);
