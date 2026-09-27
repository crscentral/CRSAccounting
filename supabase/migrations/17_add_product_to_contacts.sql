alter table public.contacts add column product public.app_product;
update public.contacts set product = 'basic' where product is null;
