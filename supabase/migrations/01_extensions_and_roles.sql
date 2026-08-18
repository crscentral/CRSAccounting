create extension if not exists "uuid-ossp";

create type public.member_role as enum ('owner', 'admin', 'accountant', 'viewer');

create table public.user_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  email text,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.companies (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  legal_name text,
  logo_url text,
  address text,
  city text,
  country text,
  email text,
  website text,
  base_currency text not null default 'USD',
  fiscal_year_start_month int not null default 1 check (fiscal_year_start_month between 1 and 12),
  bank_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.company_members (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references public.companies(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  role public.member_role not null default 'viewer',
  invited_email text,
  created_at timestamptz not null default now()
);

create or replace function public.has_company_role(p_company_id uuid, p_min_roles public.member_role[])
returns boolean language sql security definer stable as $$
  select exists (
    select 1 from public.company_members cm
    where cm.company_id = p_company_id and cm.user_id = auth.uid() and cm.role = any(p_min_roles)
  );
$$;

alter table public.user_profiles enable row level security;
alter table public.companies enable row level security;
alter table public.company_members enable row level security;

create policy "users see own profile" on public.user_profiles for select using (id = auth.uid());
create policy "users update own profile" on public.user_profiles for update using (id = auth.uid());
create policy "users insert own profile" on public.user_profiles for insert with check (id = auth.uid());

create policy "members see their companies" on public.companies for select using (
  exists (select 1 from public.company_members cm where cm.company_id = companies.id and cm.user_id = auth.uid())
);
create policy "owners/admins update company" on public.companies for update using (
  public.has_company_role(id, array['owner','admin']::public.member_role[])
);
create policy "authenticated users can create companies" on public.companies for insert with check (auth.uid() is not null);

create policy "members see company membership" on public.company_members for select using (
  exists (select 1 from public.company_members cm2 where cm2.company_id = company_members.company_id and cm2.user_id = auth.uid())
);
create policy "owners/admins manage membership" on public.company_members for all using (
  public.has_company_role(company_id, array['owner','admin']::public.member_role[])
) with check (
  public.has_company_role(company_id, array['owner','admin']::public.member_role[])
);
