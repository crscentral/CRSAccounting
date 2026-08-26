-- Fix: deleting a sales/purchase invoice left its ledger_entries orphaned (ledger
-- was a one-way sync, only auto-posting on INSERT, never cleaning up on DELETE).
create or replace function public.delete_sales_invoice_ledger_entries()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  delete from public.ledger_entries where source_type = 'sales_invoice' and source_id = old.id;
  return old;
end; $$;

create trigger trg_delete_sales_invoice_ledger
  before delete on public.sales_invoices
  for each row execute function public.delete_sales_invoice_ledger_entries();

create or replace function public.delete_purchase_invoice_ledger_entries()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  delete from public.ledger_entries where source_type = 'purchase_invoice' and source_id = old.id;
  return old;
end; $$;

create trigger trg_delete_purchase_invoice_ledger
  before delete on public.purchase_invoices
  for each row execute function public.delete_purchase_invoice_ledger_entries();

-- Also handle EDITS: previously editing an invoice never re-posted ledger entries,
-- so an edited invoice's ledger postings went stale (still showed old amount).
create or replace function public.repost_sales_invoice_to_ledger()
returns trigger language plpgsql security definer set search_path = public as $$
declare ar_id uuid; rev_id uuid;
begin
  delete from public.ledger_entries where source_type = 'sales_invoice' and source_id = new.id;
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

create trigger trg_repost_sales_invoice_ledger
  after update on public.sales_invoices
  for each row execute function public.repost_sales_invoice_to_ledger();

create or replace function public.repost_purchase_invoice_to_ledger()
returns trigger language plpgsql security definer set search_path = public as $$
declare ap_id uuid;
begin
  delete from public.ledger_entries where source_type = 'purchase_invoice' and source_id = new.id;
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

create trigger trg_repost_purchase_invoice_ledger
  after update on public.purchase_invoices
  for each row execute function public.repost_purchase_invoice_to_ledger();
