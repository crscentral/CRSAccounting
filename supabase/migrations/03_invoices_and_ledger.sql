create type public.invoice_status as enum ('Draft','Paid','Overdue','Cancelled');

create table public.sales_invoices (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references public.companies(id) on delete cascade,
  invoice_number text not null,
  contact_id uuid references public.contacts(id),
  invoice_date date not null,
  due_date date,
  currency text not null default 'USD',
  fx_rate_locked numeric(18,6) not null default 1,
  amount numeric(18,2) not null,
  amount_usd numeric(18,2) not null,
  balance_due numeric(18,2) not null,
  status public.invoice_status not null default 'Draft',
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.purchase_invoices (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references public.companies(id) on delete cascade,
  invoice_number text not null,
  contact_id uuid references public.contacts(id),
  supplier_name_freeform text,
  invoice_date date not null,
  currency text not null default 'USD',
  fx_rate_locked numeric(18,6) not null default 1,
  amount numeric(18,2) not null,
  amount_usd numeric(18,2) not null,
  account_id uuid references public.accounts(id),
  status public.invoice_status not null default 'Draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.payment_receipts (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references public.companies(id) on delete cascade,
  sales_invoice_id uuid references public.sales_invoices(id) on delete set null,
  receipt_date date not null,
  currency text not null default 'USD',
  fx_rate_locked numeric(18,6) not null default 1,
  amount numeric(18,2) not null,
  amount_usd numeric(18,2) not null,
  method text,
  created_at timestamptz not null default now()
);

create table public.ledger_entries (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references public.companies(id) on delete cascade,
  account_id uuid not null references public.accounts(id),
  entry_date date not null,
  description text,
  currency text not null default 'USD',
  fx_rate_locked numeric(18,6) not null default 1,
  debit_usd numeric(18,2) not null default 0,
  credit_usd numeric(18,2) not null default 0,
  source_type text,
  source_id uuid,
  created_at timestamptz not null default now()
);

alter table public.sales_invoices enable row level security;
alter table public.purchase_invoices enable row level security;
alter table public.payment_receipts enable row level security;
alter table public.ledger_entries enable row level security;

create policy "members view sales invoices" on public.sales_invoices for select using (
  exists (select 1 from public.company_members cm where cm.company_id = sales_invoices.company_id and cm.user_id = auth.uid())
);
create policy "accountant+ manage sales invoices" on public.sales_invoices for all using (
  public.has_company_role(company_id, array['owner','admin','accountant']::public.member_role[])
);

create policy "members view purchase invoices" on public.purchase_invoices for select using (
  exists (select 1 from public.company_members cm where cm.company_id = purchase_invoices.company_id and cm.user_id = auth.uid())
);
create policy "accountant+ manage purchase invoices" on public.purchase_invoices for all using (
  public.has_company_role(company_id, array['owner','admin','accountant']::public.member_role[])
);

create policy "members view payment receipts" on public.payment_receipts for select using (
  exists (select 1 from public.company_members cm where cm.company_id = payment_receipts.company_id and cm.user_id = auth.uid())
);
create policy "accountant+ manage payment receipts" on public.payment_receipts for all using (
  public.has_company_role(company_id, array['owner','admin','accountant']::public.member_role[])
);

create policy "members view ledger" on public.ledger_entries for select using (
  exists (select 1 from public.company_members cm where cm.company_id = ledger_entries.company_id and cm.user_id = auth.uid())
);
create policy "accountant+ manage ledger" on public.ledger_entries for all using (
  public.has_company_role(company_id, array['owner','admin','accountant']::public.member_role[])
);
