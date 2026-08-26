insert into public.companies (id, name, legal_name, address, city, country, email, website, base_currency, fiscal_year_start_month)
values ('11111111-1111-1111-1111-111111111111', 'CRS Central', 'CRS Chauhan Private Limited', 'Hyderabad', 'Hyderabad', 'India', 'info@crscentral.com', 'https://crscentral.com/', 'USD', 1);

insert into public.company_settings (company_id, favorite_currencies, default_view_currency)
values ('11111111-1111-1111-1111-111111111111', array['USD','THB','INR'], 'USD');

-- Chart of Accounts (19 accounts: 12 confirmed from screenshots + 7 standard accounts completing
-- the set, inferred from transaction descriptions -- flagged for review, see README)
insert into public.accounts (company_id, code, name, type, subtype, currency) values
('11111111-1111-1111-1111-111111111111','1010','Cash on Hand','Assets','Current Assets','USD'),
('11111111-1111-1111-1111-111111111111','1020','Accounts Receivable','Assets','Current Assets','USD'),
('11111111-1111-1111-1111-111111111111','1050','Office Equipment','Assets','Fixed Assets','USD'),
('11111111-1111-1111-1111-111111111111','2010','Accounts Payable','Liabilities','Current Liabilities','USD'),
('11111111-1111-1111-1111-111111111111','2020','Credit Card Payable','Liabilities','Current Liabilities','USD'),
('11111111-1111-1111-1111-111111111111','3010','Owner''s Contribution','Equity',null,'USD'),
('11111111-1111-1111-1111-111111111111','3020','Retained Earnings','Equity',null,'USD'),
('11111111-1111-1111-1111-111111111111','4010','Sales Revenue','Revenue',null,'USD'),
('11111111-1111-1111-1111-111111111111','4020','Service Revenue','Revenue',null,'USD'),
('11111111-1111-1111-1111-111111111111','5010','Marketing Expenses','Expenses','Operating Expenses','USD'),
('11111111-1111-1111-1111-111111111111','5011','Bank Charges','Expenses','Other Expenses','USD'),
('11111111-1111-1111-1111-111111111111','5020','Travel Expenses','Expenses','Operating Expenses','USD'),
('11111111-1111-1111-1111-111111111111','5030','Software & Subscriptions','Expenses','Operating Expenses','USD'),
('11111111-1111-1111-1111-111111111111','5040','Legal & Professional Fees','Expenses','Operating Expenses','USD'),
('11111111-1111-1111-1111-111111111111','5060','GST Expenses','Expenses','Other Expenses','USD'),
('11111111-1111-1111-1111-111111111111','5070','Chartered Accountant Expenses','Expenses','Operating Expenses','USD'),
('11111111-1111-1111-1111-111111111111','5080','Govt. Expenses','Expenses',null,'USD'),
('11111111-1111-1111-1111-111111111111','5090','GST Payment','Expenses','Other Expenses','USD'),
('11111111-1111-1111-1111-111111111111','5099','Miscellaneous Expenses','Expenses','Other Expenses','USD');

insert into public.contacts (company_id, type, name, email, phone) values
('11111111-1111-1111-1111-111111111111','customer','Dhavara Boutique Hotel','info.dhavara@gmail.com','+8562056289494'),
('11111111-1111-1111-1111-111111111111','customer','SUCHANAN SERVICE APARTMENT COMPANY LIMITED',null,null);

insert into public.contacts (company_id, type, name, email, phone, tax_id) values
('11111111-1111-1111-1111-111111111111','supplier','Experion Infotech - Marketing','experioninfotech@gmail.com','8448714767',null),
('11111111-1111-1111-1111-111111111111','supplier','ratenexus.in - Service Contract','info@ratenexus.in','+919971687971','09AFGPY3356J1ZT'),
('11111111-1111-1111-1111-111111111111','supplier','Palod and Loya - CA','info@palodandloya.com','8125306067','36AAUFP4162E1ZZ'),
('11111111-1111-1111-1111-111111111111','supplier','INDIAFILINGS PRIVATE LIMITED',null,null,'33AADCI6142F1ZX'),
('11111111-1111-1111-1111-111111111111','supplier','Hostinger PTE',null,null,'GST Reg #: 201427808M');
