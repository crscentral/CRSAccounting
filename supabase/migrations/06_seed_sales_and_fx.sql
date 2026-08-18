insert into public.fx_rates_cache (currency_code, rate_date, rate_to_usd) values
('USD', current_date, 1.0),
('THB', current_date, 33.4451),
('INR', current_date, 95.5200);

insert into public.sales_invoices (company_id, invoice_number, contact_id, invoice_date, due_date, currency, fx_rate_locked, amount, amount_usd, balance_due, status)
select '11111111-1111-1111-1111-111111111111'::uuid,'INV-004', id, '2026-08-01'::date,'2026-08-05'::date,'USD',1,800,800,800,'Draft'::public.invoice_status from public.contacts where name='Dhavara Boutique Hotel'
union all
select '11111111-1111-1111-1111-111111111111'::uuid,'INV-003', id, '2026-07-01'::date,'2026-07-05'::date,'USD',1,800,800,0,'Paid'::public.invoice_status from public.contacts where name='Dhavara Boutique Hotel'
union all
select '11111111-1111-1111-1111-111111111111'::uuid,'INV-002', id, '2026-06-02'::date,'2026-06-05'::date,'USD',1,800,800,0,'Paid'::public.invoice_status from public.contacts where name='Dhavara Boutique Hotel'
union all
select '11111111-1111-1111-1111-111111111111'::uuid,'INV-001', id, '2026-05-04'::date,'2026-05-07'::date,'USD',1,800,800,0,'Paid'::public.invoice_status from public.contacts where name='Dhavara Boutique Hotel'
union all
select '11111111-1111-1111-1111-111111111111'::uuid,'INV-001989', id, '2026-04-07'::date,'2026-04-10'::date,'USD',1,432,432,0,'Paid'::public.invoice_status from public.contacts where name='SUCHANAN SERVICE APARTMENT COMPANY LIMITED'
union all
select '11111111-1111-1111-1111-111111111111'::uuid,'INV-001', id, '2026-04-01'::date,'2026-04-09'::date,'USD',1,800,800,0,'Paid'::public.invoice_status from public.contacts where name='Dhavara Boutique Hotel'
union all
select '11111111-1111-1111-1111-111111111111'::uuid,'INV-001966', id, '2026-03-01'::date,'2026-03-05'::date,'USD',1,448,448,0,'Paid'::public.invoice_status from public.contacts where name='SUCHANAN SERVICE APARTMENT COMPANY LIMITED';

insert into public.payment_receipts (company_id, sales_invoice_id, receipt_date, currency, fx_rate_locked, amount, amount_usd, method)
select '11111111-1111-1111-1111-111111111111'::uuid, id, due_date, currency, fx_rate_locked, amount, amount_usd, 'Bank Transfer'
from public.sales_invoices where status = 'Paid';
