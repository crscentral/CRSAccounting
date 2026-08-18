create type public.account_type as enum ('Assets','Liabilities','Equity','Revenue','Expenses');

create table public.accounts (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references public.companies(id) on delete cascade,
  code text not null,
  name text not null,
  type public.account_type not null,
  subtype text,
  currency text not null default 'USD',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (company_id, code)
);

create type public.contact_type as enum ('customer', 'supplier');

create table public.contacts (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references public.companies(id) on delete cascade,
  type public.contact_type not null,
  name text not null,
  email text,
  phone text,
  tax_id text,
  address text,
  created_at timestamptz not null default now()
);

alter table public.accounts enable row level security;
alter table public.contacts enable row level security;

create policy "members view accounts" on public.accounts for select using (
  exists (select 1 from public.company_members cm where cm.company_id = accounts.company_id and cm.user_id = auth.uid())
);
create policy "accountant+ manage accounts" on public.accounts for all using (
  public.has_company_role(company_id, array['owner','admin','accountant']::public.member_role[])
);

create policy "members view contacts" on public.contacts for select using (
  exists (select 1 from public.company_members cm where cm.company_id = contacts.company_id and cm.user_id = auth.uid())
);
create policy "accountant+ manage contacts" on public.contacts for all using (
  public.has_company_role(company_id, array['owner','admin','accountant']::public.member_role[])
);
