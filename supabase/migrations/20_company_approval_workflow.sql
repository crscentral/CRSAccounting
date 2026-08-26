-- New self-service company signups must be approved by the platform owner
-- (crscentral.rm@gmail.com) before that company can use the app. Existing
-- companies (i.e. CRS Central, seeded in migration 05) are grandfathered in
-- as already-approved so nothing currently working breaks.

alter table public.companies
  add column if not exists approval_status text not null default 'pending'
    check (approval_status in ('pending', 'approved', 'rejected'));

-- Grandfather in every company that existed before this migration.
update public.companies set approval_status = 'approved' where approval_status = 'pending';

create or replace function public.is_platform_admin()
returns boolean
language sql
security definer
stable
set search_path = public
as $$
  select auth.jwt() ->> 'email' = 'crscentral.rm@gmail.com';
$$;

-- Platform admin can see every company (needed to list pending ones), on top of
-- the existing "members see their companies" policy (multiple SELECT policies
-- are OR'd together, so members still see their own).
create policy "platform admin sees all companies" on public.companies for select using (
  public.is_platform_admin()
);

-- Prevent a company's own owner/admin from approving themselves by editing the
-- row directly through the normal "owners/admins update company" policy -- only
-- the platform admin (or the approve_company() function below) may change this
-- specific column.
create or replace function public.protect_approval_status()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.approval_status is distinct from old.approval_status and not public.is_platform_admin() then
    new.approval_status := old.approval_status;
  end if;
  return new;
end;
$$;

create trigger trg_protect_approval_status
  before update on public.companies
  for each row execute function public.protect_approval_status();

create or replace function public.approve_company(p_company_id uuid, p_approve boolean default true)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.is_platform_admin() then
    raise exception 'Not authorized';
  end if;
  update public.companies
  set approval_status = case when p_approve then 'approved' else 'rejected' end
  where id = p_company_id;
end;
$$;

grant execute on function public.approve_company to authenticated;
