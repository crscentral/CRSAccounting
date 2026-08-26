-- FIX 1: Attach an ALREADY-SIGNED-UP user immediately when an Owner/Admin invites their
-- email (previously, linking only happened at signup time -- so "invite after signup"
-- silently failed to attach, leaving a dangling pending invite forever).
create or replace function public.attach_existing_user_on_invite()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare existing_user_id uuid;
begin
  if new.user_id is null and new.invited_email is not null then
    select id into existing_user_id from auth.users where email = new.invited_email limit 1;
    if existing_user_id is not null then
      new.user_id := existing_user_id;
      new.invited_email := null;
    end if;
  end if;
  return new;
end;
$$;

create trigger trg_attach_existing_user_on_invite
before insert on public.company_members
for each row execute function public.attach_existing_user_on_invite();

-- FIX 2: "New Company" needs an atomic, safe way to (a) create the company and
-- (b) make the creator its Owner -- can't just be two plain inserts from the client,
-- because the company_members write-policy requires you to ALREADY be an owner/admin
-- of a company before inserting membership rows for it. This function only ever grants
-- ownership of a BRAND-NEW company to whoever is calling it -- cannot be used to join
-- or alter any existing company.
create or replace function public.create_company_with_owner(
  p_name text,
  p_legal_name text default null,
  p_address text default null,
  p_city text default null,
  p_country text default null,
  p_email text default null,
  p_website text default null,
  p_base_currency text default 'USD',
  p_fiscal_year_start_month int default 1
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare new_company_id uuid;
begin
  if auth.uid() is null then
    raise exception 'Must be authenticated to create a company';
  end if;

  insert into public.companies (name, legal_name, address, city, country, email, website, base_currency, fiscal_year_start_month)
  values (p_name, p_legal_name, p_address, p_city, p_country, p_email, p_website,
          coalesce(p_base_currency, 'USD'), coalesce(p_fiscal_year_start_month, 1))
  returning id into new_company_id;

  insert into public.company_members (company_id, user_id, role)
  values (new_company_id, auth.uid(), 'owner');

  insert into public.company_settings (company_id)
  values (new_company_id);

  return new_company_id;
end;
$$;

grant execute on function public.create_company_with_owner to authenticated;
