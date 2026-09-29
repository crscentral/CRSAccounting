-- 1. Temp codes
UPDATE public.accounts SET code = 'T_4100' WHERE product = 'hotel' AND name = 'Room Revenue';
UPDATE public.accounts SET code = 'T_4101' WHERE product = 'hotel' AND name = 'Early Check-in / Late Check-out Revenue';
UPDATE public.accounts SET code = 'T_4102' WHERE product = 'hotel' AND name = 'Beverage Revenue';
UPDATE public.accounts SET code = 'T_4103' WHERE product = 'hotel' AND name = 'F&B Revenue';
UPDATE public.accounts SET code = 'T_5100' WHERE product = 'hotel' AND name = 'PMS Cost';
UPDATE public.accounts SET code = 'T_5101' WHERE product = 'hotel' AND name = 'Travel Agent / OTA Commissions';
UPDATE public.accounts SET code = 'T_5102' WHERE product = 'hotel' AND name = 'Stationery & Printing';
UPDATE public.accounts SET code = 'T_5103' WHERE product = 'hotel' AND name = 'F&B Service Labor';
UPDATE public.accounts SET code = 'T_5104' WHERE product = 'hotel' AND name = 'Food Cost';
UPDATE public.accounts SET code = 'T_5105' WHERE product = 'hotel' AND name = 'Software & Licensing';
UPDATE public.accounts SET code = 'T_5106' WHERE product = 'hotel' AND name = 'Accounting & Audit Fees';
UPDATE public.accounts SET code = 'T_5011' WHERE product = 'hotel' AND name = 'Bank Charges';
UPDATE public.accounts SET code = 'T_5107' WHERE product = 'hotel' AND name = 'Office Supplies';
UPDATE public.accounts SET code = 'T_5040' WHERE product = 'hotel' AND name = 'Legal & Professional Fees';
UPDATE public.accounts SET code = 'T_5108' WHERE product = 'hotel' AND name = 'Purchase Department Overhead';
UPDATE public.accounts SET code = 'T_5109' WHERE product = 'hotel' AND name = 'Inventory Shrinkage / Wastage';
UPDATE public.accounts SET code = 'T_5110' WHERE product = 'hotel' AND name = 'Digital Marketing';
UPDATE public.accounts SET code = 'T_5111' WHERE product = 'hotel' AND name = 'Print & Offline Marketing';
UPDATE public.accounts SET code = 'T_5112' WHERE product = 'hotel' AND name = 'Loyalty Program Costs';
UPDATE public.accounts SET code = 'T_5113' WHERE product = 'hotel' AND name = 'Electricity';
UPDATE public.accounts SET code = 'T_5114' WHERE product = 'hotel' AND name = 'Water';
UPDATE public.accounts SET code = 'T_5115' WHERE product = 'hotel' AND name = 'Repairs & Maintenance';
UPDATE public.accounts SET code = 'T_5116' WHERE product = 'hotel' AND name = 'Housekeeping Supplies';
UPDATE public.accounts SET code = 'T_1100' WHERE product = 'restaurant' AND name = 'Kitchen Equipment';
UPDATE public.accounts SET code = 'T_4104' WHERE product = 'restaurant' AND name = 'Food Sales';
UPDATE public.accounts SET code = 'T_4105' WHERE product = 'restaurant' AND name = 'Beverage Sales';
UPDATE public.accounts SET code = 'T_5104' WHERE product = 'restaurant' AND name = 'Food Cost';
UPDATE public.accounts SET code = 'T_5034' WHERE product = 'restaurant' AND name = 'Beverage Cost';
UPDATE public.accounts SET code = 'T_5117' WHERE product = 'restaurant' AND name = 'Management Labor';
UPDATE public.accounts SET code = 'T_5118' WHERE product = 'restaurant' AND name = 'Staff Labor';
UPDATE public.accounts SET code = 'T_5119' WHERE product = 'restaurant' AND name = 'Direct Operating Expenses';
UPDATE public.accounts SET code = 'T_5120' WHERE product = 'restaurant' AND name = 'Music & Entertainment';
UPDATE public.accounts SET code = 'T_5121' WHERE product = 'restaurant' AND name = 'Marketing';
UPDATE public.accounts SET code = 'T_5122' WHERE product = 'restaurant' AND name = 'Utilities';
UPDATE public.accounts SET code = 'T_5123' WHERE product = 'restaurant' AND name = 'General & Administrative';
UPDATE public.accounts SET code = 'T_5115' WHERE product = 'restaurant' AND name = 'Repairs & Maintenance';
UPDATE public.accounts SET code = 'T_5203' WHERE product = 'restaurant' AND name = 'Rent / Lease Payment';
UPDATE public.accounts SET code = 'T_5124' WHERE product = 'restaurant' AND name = 'Property Insurance';
UPDATE public.accounts SET code = 'T_5125' WHERE product = 'restaurant' AND name = 'Property Taxes';
UPDATE public.accounts SET code = 'T_5126' WHERE product = 'restaurant' AND name = 'License & Government Fees';
UPDATE public.accounts SET code = 'T_5127' WHERE product = 'restaurant' AND name = 'AMC (Annual Maintenance Contracts)';
UPDATE public.accounts SET code = 'T_5206' WHERE product = 'restaurant' AND name = 'Depreciation & Amortization';
UPDATE public.accounts SET code = 'T_5207' WHERE product = 'restaurant' AND name = 'Loan Interest';

-- 2. Final codes
UPDATE public.accounts SET code = '4100' WHERE product = 'hotel' AND name = 'Room Revenue';
UPDATE public.accounts SET code = '4101' WHERE product = 'hotel' AND name = 'Early Check-in / Late Check-out Revenue';
UPDATE public.accounts SET code = '4102' WHERE product = 'hotel' AND name = 'Beverage Revenue';
UPDATE public.accounts SET code = '4103' WHERE product = 'hotel' AND name = 'F&B Revenue';
UPDATE public.accounts SET code = '5100' WHERE product = 'hotel' AND name = 'PMS Cost';
UPDATE public.accounts SET code = '5101' WHERE product = 'hotel' AND name = 'Travel Agent / OTA Commissions';
UPDATE public.accounts SET code = '5102' WHERE product = 'hotel' AND name = 'Stationery & Printing';
UPDATE public.accounts SET code = '5103' WHERE product = 'hotel' AND name = 'F&B Service Labor';
UPDATE public.accounts SET code = '5104' WHERE product = 'hotel' AND name = 'Food Cost';
UPDATE public.accounts SET code = '5105' WHERE product = 'hotel' AND name = 'Software & Licensing';
UPDATE public.accounts SET code = '5106' WHERE product = 'hotel' AND name = 'Accounting & Audit Fees';
UPDATE public.accounts SET code = '5011' WHERE product = 'hotel' AND name = 'Bank Charges';
UPDATE public.accounts SET code = '5107' WHERE product = 'hotel' AND name = 'Office Supplies';
UPDATE public.accounts SET code = '5040' WHERE product = 'hotel' AND name = 'Legal & Professional Fees';
UPDATE public.accounts SET code = '5108' WHERE product = 'hotel' AND name = 'Purchase Department Overhead';
UPDATE public.accounts SET code = '5109' WHERE product = 'hotel' AND name = 'Inventory Shrinkage / Wastage';
UPDATE public.accounts SET code = '5110' WHERE product = 'hotel' AND name = 'Digital Marketing';
UPDATE public.accounts SET code = '5111' WHERE product = 'hotel' AND name = 'Print & Offline Marketing';
UPDATE public.accounts SET code = '5112' WHERE product = 'hotel' AND name = 'Loyalty Program Costs';
UPDATE public.accounts SET code = '5113' WHERE product = 'hotel' AND name = 'Electricity';
UPDATE public.accounts SET code = '5114' WHERE product = 'hotel' AND name = 'Water';
UPDATE public.accounts SET code = '5115' WHERE product = 'hotel' AND name = 'Repairs & Maintenance';
UPDATE public.accounts SET code = '5116' WHERE product = 'hotel' AND name = 'Housekeeping Supplies';
UPDATE public.accounts SET code = '1100' WHERE product = 'restaurant' AND name = 'Kitchen Equipment';
UPDATE public.accounts SET code = '4104' WHERE product = 'restaurant' AND name = 'Food Sales';
UPDATE public.accounts SET code = '4105' WHERE product = 'restaurant' AND name = 'Beverage Sales';
UPDATE public.accounts SET code = '5104' WHERE product = 'restaurant' AND name = 'Food Cost';
UPDATE public.accounts SET code = '5034' WHERE product = 'restaurant' AND name = 'Beverage Cost';
UPDATE public.accounts SET code = '5117' WHERE product = 'restaurant' AND name = 'Management Labor';
UPDATE public.accounts SET code = '5118' WHERE product = 'restaurant' AND name = 'Staff Labor';
UPDATE public.accounts SET code = '5119' WHERE product = 'restaurant' AND name = 'Direct Operating Expenses';
UPDATE public.accounts SET code = '5120' WHERE product = 'restaurant' AND name = 'Music & Entertainment';
UPDATE public.accounts SET code = '5121' WHERE product = 'restaurant' AND name = 'Marketing';
UPDATE public.accounts SET code = '5122' WHERE product = 'restaurant' AND name = 'Utilities';
UPDATE public.accounts SET code = '5123' WHERE product = 'restaurant' AND name = 'General & Administrative';
UPDATE public.accounts SET code = '5115' WHERE product = 'restaurant' AND name = 'Repairs & Maintenance';
UPDATE public.accounts SET code = '5203' WHERE product = 'restaurant' AND name = 'Rent / Lease Payment';
UPDATE public.accounts SET code = '5124' WHERE product = 'restaurant' AND name = 'Property Insurance';
UPDATE public.accounts SET code = '5125' WHERE product = 'restaurant' AND name = 'Property Taxes';
UPDATE public.accounts SET code = '5126' WHERE product = 'restaurant' AND name = 'License & Government Fees';
UPDATE public.accounts SET code = '5127' WHERE product = 'restaurant' AND name = 'AMC (Annual Maintenance Contracts)';
UPDATE public.accounts SET code = '5206' WHERE product = 'restaurant' AND name = 'Depreciation & Amortization';
UPDATE public.accounts SET code = '5207' WHERE product = 'restaurant' AND name = 'Loan Interest';


-- 2. Create trigger to seed accounts for new companies
create or replace function public.seed_default_accounts()
returns trigger language plpgsql security definer as $$
begin
  insert into public.accounts (company_id, product, code, name, type, subtype, currency)
  values
  (new.id, 'basic', '1010', 'Cash on Hand', 'Assets', 'Current Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '1020', 'Accounts Receivable', 'Assets', 'Current Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '1050', 'Office Equipment', 'Assets', 'Fixed Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '2010', 'Accounts Payable', 'Liabilities', 'Current Liabilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '2020', 'Credit Card Payable', 'Liabilities', 'Current Liabilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '3010', 'Owner''s Contribution', 'Equity', null, coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '3020', 'Retained Earnings', 'Equity', null, coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '4010', 'Sales Revenue', 'Revenue', null, coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '4020', 'Service Revenue', 'Revenue', null, coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5010', 'Marketing Expenses', 'Expenses', 'Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5011', 'Bank Charges', 'Expenses', 'Other Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5012', 'Contracted Employment', 'Expenses', 'Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5020', 'Travel Expenses', 'Expenses', 'Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5030', 'Software & Subscriptions', 'Expenses', 'Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5040', 'Legal & Professional Fees', 'Expenses', 'Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5060', 'GST Expenses', 'Expenses', 'Other Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5070', 'Chartered Accountant Expenses', 'Expenses', 'Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5080', 'Govt. Expenses', 'Expenses', 'Govt. Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5090', 'GST Payment', 'Expenses', 'Other Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'basic', '5099', 'Miscellaneous Expenses', 'Expenses', 'Other Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '1010', 'Cash on Hand', 'Assets', 'Current Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '1020', 'Accounts Receivable', 'Assets', 'Current Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '1050', 'Office Equipment', 'Assets', 'Fixed Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '2010', 'Accounts Payable', 'Liabilities', 'Current Liabilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '2020', 'Credit Card Payable', 'Liabilities', 'Current Liabilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '2030', 'Loan Payable', 'Liabilities', 'Long-Term Liabilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '3010', 'Owner''s Contribution', 'Equity', null, coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '3020', 'Retained Earnings', 'Equity', null, coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4100', 'Room Revenue', 'Revenue', 'Front Office', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4011', 'Restaurant Food Revenue', 'Revenue', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4101', 'Early Check-in / Late Check-out Revenue', 'Revenue', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4012', 'Extra Bed Revenue', 'Revenue', 'Other Revenue', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4013', 'Miscellaneous Rooms Revenue', 'Revenue', 'Room Revenue', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4014', 'Early Check-in Revenue', 'Revenue', 'Room Revenue', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4015', 'Late Check-out Revenue', 'Revenue', 'Front Office', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4016', 'Breakfast Revenue', 'Revenue', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4017', 'Transportation Revenue', 'Revenue', 'Other Revenue', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4018', 'SPA Revenue', 'Revenue', 'Other Revenue', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4102', 'Beverage Revenue', 'Revenue', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4103', 'F&B Revenue', 'Revenue', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '4021', 'Other F&B Revenue', 'Revenue', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5100', 'PMS Cost', 'Expenses', 'Front Office', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5101', 'Travel Agent / OTA Commissions', 'Expenses', 'Front Office', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5102', 'Stationery & Printing', 'Expenses', 'Front Office', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5013', 'Guest Amenities & Service Recovery', 'Expenses', 'Front Office', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5014', 'Linen & Laundry', 'Expenses', 'Front Office', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5103', 'F&B Service Labor', 'Expenses', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5021', 'F&B Service Supplies', 'Expenses', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5104', 'Food Cost', 'Expenses', 'Kitchen', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5031', 'Kitchen Labor', 'Expenses', 'Kitchen', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5032', 'Kitchen Fuel & Gas', 'Expenses', 'Kitchen', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5033', 'Kitchen Supplies & Smallwares', 'Expenses', 'Kitchen', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5034', 'Beverage Cost', 'Expenses', 'Kitchen', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5105', 'Software & Licensing', 'Expenses', 'Technology (IT)', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5041', 'Internet & Networking', 'Expenses', 'Technology (IT)', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5042', 'IT Hardware & Maintenance', 'Expenses', 'Technology (IT)', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5050', 'Recruitment', 'Expenses', 'Human Resources (HR)', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5051', 'Training & Development', 'Expenses', 'Human Resources (HR)', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5052', 'Staff Welfare & Uniforms', 'Expenses', 'Human Resources (HR)', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5106', 'Accounting & Audit Fees', 'Expenses', 'Finance', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5011', 'Bank Charges', 'Expenses', 'Finance', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5107', 'Office Supplies', 'Expenses', 'Admin', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5040', 'Legal & Professional Fees', 'Expenses', 'Admin', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5072', 'Admin Salaries', 'Expenses', 'Admin', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5108', 'Purchase Department Overhead', 'Expenses', 'Purchase', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5081', 'Freight & Delivery Charges', 'Expenses', 'Purchase', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5109', 'Inventory Shrinkage / Wastage', 'Expenses', 'Stores', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5091', 'Storage & Warehousing', 'Expenses', 'Stores', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5110', 'Digital Marketing', 'Expenses', 'Sales & Marketing', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5111', 'Print & Offline Marketing', 'Expenses', 'Sales & Marketing', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5112', 'Loyalty Program Costs', 'Expenses', 'Sales & Marketing', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5113', 'Electricity', 'Expenses', 'Property Ops & Utilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5114', 'Water', 'Expenses', 'Property Ops & Utilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5115', 'Repairs & Maintenance', 'Expenses', 'Property Ops & Utilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5116', 'Housekeeping Supplies', 'Expenses', 'Property Ops & Utilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5200', 'Management Fees', 'Expenses', 'Below GOP', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5201', 'Property Tax', 'Expenses', 'Below GOP', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5202', 'Insurance', 'Expenses', 'Below GOP', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5203', 'Rent / Lease Payment', 'Expenses', 'Below GOP', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5204', 'License Fees', 'Expenses', 'Below GOP', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5205', 'Government Fees & Taxes', 'Expenses', 'Below GOP', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5206', 'Depreciation & Amortization', 'Expenses', 'Below GOP', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5207', 'Loan Interest', 'Expenses', 'Below GOP', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5300', 'Man Power Monthly Cost', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5301', 'AMC (Annual Maintenance Contract)', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5302', 'Outsourced Employment Contract', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5303', 'Maintenance Daily Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5304', 'Maintenance Monthly Expenses', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5305', 'Equipment Purchases', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5306', 'Water Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5307', 'Electricity Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5308', 'Gas Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5309', 'Fuel Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5310', 'Stationary Expenses', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5311', 'Travel Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5312', 'Annual Licence and Govt Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5313', 'Software Expenses', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5314', 'Consultancy Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5315', 'Amenities Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5316', 'Housekeeping Cleaning Expenses', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5317', 'Monthly Contracts (Pest etc)', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5318', 'Laundry Cost', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5319', 'Linen Expenses', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5320', 'Uniform Expense', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'hotel', '5321', 'Other Expenses', 'Expenses', 'Hotel Operating Expenses', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '1010', 'Cash on Hand', 'Assets', 'Current Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '1020', 'Accounts Receivable', 'Assets', 'Current Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '1100', 'Kitchen Equipment', 'Assets', 'Fixed Assets', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '2010', 'Accounts Payable', 'Liabilities', 'Current Liabilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '2020', 'Credit Card Payable', 'Liabilities', 'Current Liabilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '2030', 'Loan Payable', 'Liabilities', 'Long-Term Liabilities', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '3010', 'Owner''s Contribution', 'Equity', null, coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '3020', 'Retained Earnings', 'Equity', null, coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '4104', 'Food Sales', 'Revenue', 'F&B Revenue', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '4105', 'Beverage Sales', 'Revenue', 'F&B Service', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '4016', 'Breakfast Revenue', 'Revenue', 'F&B Revenue', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '4019', 'Other Operating Income', 'Revenue', 'Other Revenue', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5104', 'Food Cost', 'Expenses', 'Cost of Sales', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5034', 'Beverage Cost', 'Expenses', 'Cost of Sales', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5117', 'Management Labor', 'Expenses', 'Labor', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5118', 'Staff Labor', 'Expenses', 'Labor', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5022', 'Payroll Taxes & Employee Benefits', 'Expenses', 'Labor', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5119', 'Direct Operating Expenses', 'Expenses', 'Other Controllable', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5120', 'Music & Entertainment', 'Expenses', 'Other Controllable', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5121', 'Marketing', 'Expenses', 'Other Controllable', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5122', 'Utilities', 'Expenses', 'Other Controllable', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5123', 'General & Administrative', 'Expenses', 'Other Controllable', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5115', 'Repairs & Maintenance', 'Expenses', 'Other Controllable', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5203', 'Rent / Lease Payment', 'Expenses', 'Occupancy', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5124', 'Property Insurance', 'Expenses', 'Occupancy', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5125', 'Property Taxes', 'Expenses', 'Occupancy', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5126', 'License & Government Fees', 'Expenses', 'Occupancy', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5127', 'AMC (Annual Maintenance Contracts)', 'Expenses', 'Occupancy', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5206', 'Depreciation & Amortization', 'Expenses', 'Below EBITDA', coalesce(new.base_currency, 'USD')),
  (new.id, 'restaurant', '5207', 'Loan Interest', 'Expenses', 'Below EBITDA', coalesce(new.base_currency, 'USD'));
  return new;
end;
$$;

drop trigger if exists trg_seed_default_accounts on public.companies;
create trigger trg_seed_default_accounts
  after insert on public.companies
  for each row execute function public.seed_default_accounts();
