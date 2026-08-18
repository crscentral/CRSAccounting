-- Correction: the two Suchanan Service Apartment invoices were actually in THB, not USD,
-- per the currency breakdown on the original Sales & Receipts screenshot.
update public.sales_invoices
set currency = 'THB', fx_rate_locked = 33.4451, amount = round(amount_usd * 33.4451, 2)
where invoice_number in ('INV-001989','INV-001966');
