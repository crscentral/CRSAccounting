create table public.fx_rates_cache (
  id uuid primary key default uuid_generate_v4(),
  currency_code text not null,
  rate_date date not null,
  rate_to_usd numeric(18,6) not null,
  created_at timestamptz not null default now(),
  unique (currency_code, rate_date)
);

create table public.forecast_entries (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references public.companies(id) on delete cascade,
  forecast_year int not null,
  forecast_month int not null check (forecast_month between 1 and 12),
  revenue_usd numeric(18,2) not null default 0,
  expenses_usd numeric(18,2) not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (company_id, forecast_year, forecast_month)
);

create table public.company_settings (
  company_id uuid primary key references public.companies(id) on delete cascade,
  favorite_currencies text[] not null default array['USD','THB','INR'],
  default_view_currency text not null default 'USD',
  updated_at timestamptz not null default now()
);

alter table public.fx_rates_cache enable row level security;
alter table public.forecast_entries enable row level security;
alter table public.company_settings enable row level security;

create policy "authenticated users read fx rates" on public.fx_rates_cache for select using (auth.uid() is not null);
create policy "service role writes fx rates" on public.fx_rates_cache for insert with check (auth.uid() is not null);
create policy "service role updates fx rates" on public.fx_rates_cache for update using (auth.uid() is not null);

create policy "members view forecast" on public.forecast_entries for select using (
  exists (select 1 from public.company_members cm where cm.company_id = forecast_entries.company_id and cm.user_id = auth.uid())
);
create policy "accountant+ manage forecast" on public.forecast_entries for all using (
  public.has_company_role(company_id, array['owner','admin','accountant']::public.member_role[])
);

create policy "members view settings" on public.company_settings for select using (
  exists (select 1 from public.company_members cm where cm.company_id = company_settings.company_id and cm.user_id = auth.uid())
);
create policy "owner/admin manage settings" on public.company_settings for all using (
  public.has_company_role(company_id, array['owner','admin']::public.member_role[])
);
