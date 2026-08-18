-- Root cause: several SELECT policies checked "is this user a member of this company"
-- by querying company_members directly inside company_members' own policy (and inside
-- every other table's policy). That's circular -- Postgres detects it and refuses to run
-- the query at all. Fix: do that check inside a SECURITY DEFINER function, which runs
-- with elevated privileges and bypasses RLS internally, breaking the loop.

create or replace function public.is_company_member(p_company_id uuid)
returns boolean
language sql
security definer
stable
set search_path = public
as $$
  select exists (
    select 1 from public.company_members cm
    where cm.company_id = p_company_id and cm.user_id = auth.uid()
  );
$$;

drop policy if exists "members see company membership" on public.company_members;
create policy "members see company membership" on public.company_members for select using (
  public.is_company_member(company_id)
);

drop policy if exists "members see their companies" on public.companies;
create policy "members see their companies" on public.companies for select using (
  public.is_company_member(id)
);

drop policy if exists "members view accounts" on public.accounts;
create policy "members view accounts" on public.accounts for select using (
  public.is_company_member(company_id)
);

drop policy if exists "members view contacts" on public.contacts;
create policy "members view contacts" on public.contacts for select using (
  public.is_company_member(company_id)
);

drop policy if exists "members view sales invoices" on public.sales_invoices;
create policy "members view sales invoices" on public.sales_invoices for select using (
  public.is_company_member(company_id)
);

drop policy if exists "members view purchase invoices" on public.purchase_invoices;
create policy "members view purchase invoices" on public.purchase_invoices for select using (
  public.is_company_member(company_id)
);

drop policy if exists "members view payment receipts" on public.payment_receipts;
create policy "members view payment receipts" on public.payment_receipts for select using (
  public.is_company_member(company_id)
);

drop policy if exists "members view ledger" on public.ledger_entries;
create policy "members view ledger" on public.ledger_entries for select using (
  public.is_company_member(company_id)
);

drop policy if exists "members view forecast" on public.forecast_entries;
create policy "members view forecast" on public.forecast_entries for select using (
  public.is_company_member(company_id)
);

drop policy if exists "members view settings" on public.company_settings;
create policy "members view settings" on public.company_settings for select using (
  public.is_company_member(company_id)
);

create or replace function public.has_company_role(p_company_id uuid, p_min_roles public.member_role[])
returns boolean
language sql
security definer
stable
set search_path = public
as $$
  select exists (
    select 1 from public.company_members cm
    where cm.company_id = p_company_id
      and cm.user_id = auth.uid()
      and cm.role = any(p_min_roles)
  );
$$;
