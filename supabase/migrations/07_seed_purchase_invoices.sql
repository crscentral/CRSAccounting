-- Purchase invoices: currency amounts as shown in the source screenshots; amount_usd computed
-- using flat rates (INR 95.52, THB 33.4451, USD 1) since real historical daily rates weren't
-- available. See README "Data accuracy notes".
with acc as (select id, code from public.accounts),
     con as (select id, name from public.contacts)
insert into public.purchase_invoices (company_id, invoice_number, contact_id, supplier_name_freeform, invoice_date, currency, fx_rate_locked, amount, amount_usd, account_id, status)
select '11111111-1111-1111-1111-111111111111'::uuid, v.inv_no, con.id, v.freeform, v.dt::date, v.cur,
       case v.cur when 'INR' then 95.52 when 'THB' then 33.4451 else 1 end,
       v.amt,
       round(v.amt / (case v.cur when 'INR' then 95.52 when 'THB' then 33.4451 else 1 end), 2),
       acc.id,
       v.status::public.invoice_status
from (values
  ('PI-TXN-1785576209153','2026-08-31','Palod and Loya - CA',null,'INR',4720.00,'5070','Draft'),
  ('PI-TXN-1785576262279','2026-08-31','ratenexus.in - Service Contract',null,'INR',11800.00,'5010','Draft'),
  ('PI-TXN-1783526853247','2026-07-31','ratenexus.in - Service Contract',null,'INR',11800.00,'5010','Draft'),
  ('PI-TXN-1783526762181','2026-07-30','Palod and Loya - CA',null,'INR',4720.00,'5070','Draft'),
  ('PI-TXN-1785575731600','2026-07-29',null,'Adds July','INR',2200.00,'5010','Paid'),
  ('PI-TXN-1783527280531','2026-07-08',null,'Bank Charges - USD to INR','INR',886.14,'5011','Paid'),
  ('PI-TXN-1783527125529','2026-07-06',null,'Bank Charges KIP to USD','USD',12.00,'5011','Paid'),
  ('PL/R-206/26-27','2026-06-30','Palod and Loya - CA',null,'INR',4720.00,'5070','Paid'),
  ('2026-27-038','2026-06-30','ratenexus.in - Service Contract',null,'INR',11800.00,'5010','Paid'),
  ('PI-TXN-1783529527324','2026-06-26',null,'Adds June','INR',1200.00,'5010','Paid'),
  ('PI-TXN-1783529446275','2026-06-18',null,'Adds June','INR',1100.00,'5010','Paid'),
  ('PI-TXN-1783529403659','2026-06-16',null,'Adds June','INR',1500.00,'5010','Paid'),
  ('PI-TXN-1783532804103','2026-06-15',null,'GST Repayment','INR',2030.00,'5060','Draft'),
  ('PI-TXN-1783532687654','2026-06-15',null,'GST Expenses','INR',3000.00,'5060','Paid'),
  ('PI-TXN-1780995749886','2026-06-08',null,'Bank Charges - USD to INR','INR',882.99,'5011','Paid'),
  ('PI-TXN-1780995444804','2026-06-06',null,'Bank Charges KIP to USD','USD',12.00,'5011','Paid'),
  ('2026-27-021','2026-05-31','ratenexus.in - Service Contract',null,'INR',11797.00,'5010','Paid'),
  ('PL/R-152/26-27','2026-05-30','Palod and Loya - CA',null,'INR',4720.00,'5070','Paid'),
  ('PI-TXN-1780994194866','2026-05-28',null,'Laos Dhavara Visit 2','THB',5940.00,'5020','Paid'),
  ('PI-TXN-1778073983981','2026-05-07',null,'Bank Charges - USD to INR','INR',878.93,'5011','Paid'),
  ('PI-TXN-1778072545897','2026-05-06',null,'Bank Charges KIP to USD','USD',12.00,'5011','Paid'),
  ('PI-TXN-1778073343376','2026-05-01','Experion Infotech - Marketing',null,'INR',1359.36,'5010','Paid'),
  ('PI-TXN-1778073371258','2026-05-01','Experion Infotech - Marketing',null,'INR',4000.08,'5010','Paid'),
  ('PL/R-107/26-27','2026-04-30','Palod and Loya - CA',null,'INR',4720.00,'5070','Paid'),
  ('2026-27-017','2026-04-30','ratenexus.in - Service Contract',null,'INR',35400.00,'5010','Paid'),
  ('PI-TXN-1778073310026','2026-04-25','Experion Infotech - Marketing',null,'INR',2300.00,'5010','Paid'),
  ('PI-TXN-1776269812362','2026-04-14','Experion Infotech - Marketing',null,'INR',6000.00,'5010','Paid'),
  ('PI-TXN-1776589084684','2026-04-10',null,'Bank Charges - USD to INR','INR',862.58,'5011','Paid'),
  ('PI-TXN-1776588876043','2026-04-10',null,'Bank Charges KIP to USD','USD',12.00,'5011','Paid'),
  ('2025-26-220','2026-03-31','ratenexus.in - Service Contract',null,'INR',23600.00,'5010','Paid'),
  ('PI-TXN-1776575377293','2026-03-28',null,'Travel to Dhavara Vientiane Laos','THB',4500.00,'5020','Paid'),
  ('PI-TXN-1776575092257','2026-03-21',null,'Travel to Rocka Villa Samui','THB',6000.00,'5020','Paid'),
  ('PI-TXN-1776269228974','2026-03-13','Experion Infotech - Marketing',null,'INR',4000.00,'5010','Paid'),
  ('2026-9801','2026-02-20','INDIAFILINGS PRIVATE LIMITED',null,'INR',3330.82,'5040','Paid'),
  ('PI-TXN-1776574884098','2026-02-15',null,'Travel to SCN Hotel & Resort Rayong','THB',3000.00,'5020','Paid'),
  ('PI-TXN-1776269098003','2026-02-15','Experion Infotech - Marketing',null,'INR',10000.00,'5010','Paid'),
  ('PI-TXN-1776269042486','2026-02-13','Experion Infotech - Marketing',null,'INR',6000.00,'5010','Paid'),
  ('PI-TXN-1776268971818','2026-01-02','Experion Infotech - Marketing',null,'INR',3000.00,'5010','Paid'),
  ('PI-TXN-1776268915752','2026-01-01','Experion Infotech - Marketing',null,'INR',6000.00,'5010','Paid'),
  ('PL/URD-329/25-26','2025-12-03','Palod and Loya - CA',null,'INR',5900.00,'5070','Paid'),
  ('2025-64375','2025-11-01','INDIAFILINGS PRIVATE LIMITED',null,'INR',7170.50,'5040','Paid'),
  ('HSG-5992191','2025-10-24','Hostinger PTE',null,'THB',1489.44,'5030','Paid'),
  ('HSG-5992206','2025-10-24','Hostinger PTE',null,'THB',1258.84,'5030','Paid')
) as v(inv_no, dt, cname, freeform, cur, amt, acode, status)
left join con on con.name = v.cname
left join acc on acc.code = v.acode;
