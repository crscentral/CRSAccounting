create or replace function public.create_company_with_owner(
  p_name text,
  p_legal_name text default null,
  p_address text default null,
  p_city text default null,
  p_country text default null,
  p_email text default null,
  p_website text default null,
  p_base_currency text default 'USD',
  p_fiscal_year_start_month int default 1
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare 
  new_company_id uuid;
  user_email text;
  is_admin boolean;
  has_other_companies boolean;
  final_status text;
begin
  if auth.uid() is null then
    raise exception 'Must be authenticated to create a company';
  end if;

  select email into user_email from auth.users where id = auth.uid();
  is_admin := public.is_platform_admin();
  
  select exists (
    select 1 from public.company_members where user_id = auth.uid()
  ) into has_other_companies;

  -- If it's the platform admin OR the user already has at least one company, auto-approve
  if is_admin or has_other_companies then
    final_status := 'approved';
  else
    final_status := 'pending';
  end if;

  insert into public.companies (
    name, legal_name, address, city, country, email, website, 
    base_currency, fiscal_year_start_month, approval_status
  )
  values (
    p_name, p_legal_name, p_address, p_city, p_country, p_email, p_website,
    coalesce(p_base_currency, 'USD'), coalesce(p_fiscal_year_start_month, 1), final_status
  )
  returning id into new_company_id;

  -- Create the owner member for this new company, defaulting to whatever products they will get
  insert into public.company_members (company_id, user_id, role)
  values (new_company_id, auth.uid(), 'owner');

  insert into public.company_settings (company_id)
  values (new_company_id);

  if final_status = 'approved' then
    if is_admin then
      insert into public.company_products (company_id, product)
      values 
        (new_company_id, 'basic'),
        (new_company_id, 'hotel'),
        (new_company_id, 'restaurant')
      on conflict do nothing;
    else
      -- Grant access ONLY to the modules this specific user ACTUALLY has access to across their other companies
      -- (Intersection of the company's products AND their specific member products)
      insert into public.company_products (company_id, product)
      select distinct new_company_id, cp.product
      from public.company_members cm
      join public.company_products cp on cm.company_id = cp.company_id
      where cm.user_id = auth.uid()
        and cp.product = any(cm.products)
      on conflict do nothing;
    end if;
  end if;

  return new_company_id;
end;
$$;
