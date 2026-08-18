-- Fix: migration 12 changed company_members' unique constraint to a partial index
-- (WHERE user_id IS NOT NULL), but the handle_new_user() trigger's ON CONFLICT clause
-- wasn't updated to match -- causing every owner-email signup to fail.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.user_profiles (id, full_name, email)
  values (new.id, coalesce(new.raw_user_meta_data->>'full_name', new.email), new.email);

  if new.email = 'crscentral.rm@gmail.com' then
    insert into public.company_members (company_id, user_id, role)
    values ('11111111-1111-1111-1111-111111111111', new.id, 'owner')
    on conflict (company_id, user_id) where user_id is not null do nothing;
  end if;

  update public.company_members
  set user_id = new.id, invited_email = null
  where invited_email = new.email and user_id is null;

  return new;
end;
$$;
