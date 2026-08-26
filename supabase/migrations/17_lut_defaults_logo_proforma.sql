alter table public.companies
  add column if not exists industry text default 'Revenue Management',
  add column if not exists logo_url text,
  add column if not exists lut_ack_number text,
  add column if not exists lut_expiry_date date;

alter table public.sales_invoices
  add column if not exists invoice_type text default 'sales'; -- 'sales' | 'proforma'

-- Proforma invoices are not real revenue yet -- must NOT post to the ledger.
create or replace function public.post_sales_invoice_to_ledger()
returns trigger language plpgsql security definer set search_path = public as $$
declare ar_id uuid; rev_id uuid;
begin
  if new.invoice_type = 'proforma' then
    return new;
  end if;
  select id into ar_id from public.accounts where company_id = new.company_id and code = '1020' limit 1;
  select id into rev_id from public.accounts where company_id = new.company_id and code = '4010' limit 1;
  if ar_id is not null then
    insert into public.ledger_entries (company_id, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
    values (new.company_id, ar_id, new.invoice_date, 'Sales Invoice ' || new.invoice_number, new.currency, new.fx_rate_locked, new.amount_usd, 0, 'sales_invoice', new.id);
  end if;
  if rev_id is not null then
    insert into public.ledger_entries (company_id, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
    values (new.company_id, rev_id, new.invoice_date, 'Sales Invoice ' || new.invoice_number, new.currency, new.fx_rate_locked, 0, new.amount_usd, 'sales_invoice', new.id);
  end if;
  return new;
end; $$;

update public.companies set
  lut_ack_number = 'AD3603260232890',
  lut_expiry_date = '2027-03-30',
  industry = 'Revenue Management'
where name = 'CRS Central';
