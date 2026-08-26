create or replace function public.post_sales_invoice_to_ledger()
returns trigger language plpgsql security definer set search_path = public as $$
declare ar_id uuid; rev_id uuid;
begin
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

create trigger trg_post_sales_invoice after insert on public.sales_invoices
  for each row execute function public.post_sales_invoice_to_ledger();

create or replace function public.post_purchase_invoice_to_ledger()
returns trigger language plpgsql security definer set search_path = public as $$
declare ap_id uuid;
begin
  select id into ap_id from public.accounts where company_id = new.company_id and code = '2010' limit 1;
  if new.account_id is not null then
    insert into public.ledger_entries (company_id, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
    values (new.company_id, new.account_id, new.invoice_date, 'Purchase Invoice ' || new.invoice_number, new.currency, new.fx_rate_locked, new.amount_usd, 0, 'purchase_invoice', new.id);
  end if;
  if ap_id is not null then
    insert into public.ledger_entries (company_id, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
    values (new.company_id, ap_id, new.invoice_date, 'Purchase Invoice ' || new.invoice_number, new.currency, new.fx_rate_locked, 0, new.amount_usd, 'purchase_invoice', new.id);
  end if;
  return new;
end; $$;

create trigger trg_post_purchase_invoice after insert on public.purchase_invoices
  for each row execute function public.post_purchase_invoice_to_ledger();

-- Backfill for invoices seeded before these triggers existed
insert into public.ledger_entries (company_id, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
select company_id, (select id from public.accounts where company_id = si.company_id and code = '1020'),
       invoice_date, 'Sales Invoice ' || invoice_number, currency, fx_rate_locked, amount_usd, 0, 'sales_invoice', id
from public.sales_invoices si;

insert into public.ledger_entries (company_id, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
select company_id, (select id from public.accounts where company_id = si.company_id and code = '4010'),
       invoice_date, 'Sales Invoice ' || invoice_number, currency, fx_rate_locked, 0, amount_usd, 'sales_invoice', id
from public.sales_invoices si;

insert into public.ledger_entries (company_id, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
select company_id, account_id, invoice_date, 'Purchase Invoice ' || invoice_number, currency, fx_rate_locked, amount_usd, 0, 'purchase_invoice', id
from public.purchase_invoices where account_id is not null;

insert into public.ledger_entries (company_id, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
select company_id, (select id from public.accounts where company_id = pi.company_id and code = '2010'),
       invoice_date, 'Purchase Invoice ' || invoice_number, currency, fx_rate_locked, 0, amount_usd, 'purchase_invoice', id
from public.purchase_invoices pi;
