-- One-time cleanup: migration 18 added cascade-delete triggers so future invoice
-- deletes clean up their ledger_entries. Any invoice deleted BEFORE that migration
-- was applied left its ledger_entries behind as orphans (e.g. the test invoice
-- INV-610839 that still shows up under Account Ledger with no matching Sales Invoice).
-- This removes any ledger_entries whose source invoice no longer exists.

delete from public.ledger_entries le
where le.source_type = 'sales_invoice'
  and not exists (select 1 from public.sales_invoices si where si.id = le.source_id);

delete from public.ledger_entries le
where le.source_type = 'purchase_invoice'
  and not exists (select 1 from public.purchase_invoices pi where pi.id = le.source_id);
