alter table public.company_members alter column user_id drop not null;
alter table public.company_members drop constraint if exists company_members_company_id_user_id_key;
create unique index company_members_company_user_unique on public.company_members (company_id, user_id) where user_id is not null;
create unique index company_members_company_invited_email_unique on public.company_members (company_id, invited_email) where invited_email is not null and user_id is null;

alter table public.company_members
  add constraint company_members_user_or_email check (user_id is not null or invited_email is not null);

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.user_profiles (id, full_name, email)
  values (new.id, coalesce(new.raw_user_meta_data->>'full_name', new.email), new.email);

  if new.email = 'crscentral.rm@gmail.com' then
    insert into public.company_members (company_id, user_id, role)
    values ('11111111-1111-1111-1111-111111111111', new.id, 'owner')
    on conflict (company_id, user_id) do nothing;
  end if;

  update public.company_members
  set user_id = new.id, invited_email = null
  where invited_email = new.email and user_id is null;

  return new;
end;
$$;

drop policy if exists "owners/admins manage membership" on public.company_members;
create policy "owners/admins manage membership" on public.company_members for all using (
  public.has_company_role(company_id, array['owner','admin']::public.member_role[])
) with check (
  public.has_company_role(company_id, array['owner','admin']::public.member_role[])
);
