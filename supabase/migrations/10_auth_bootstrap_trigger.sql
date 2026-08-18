create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.user_profiles (id, full_name, email)
  values (new.id, coalesce(new.raw_user_meta_data->>'full_name', new.email), new.email);

  if new.email = 'crscentral.rm@gmail.com' then
    insert into public.company_members (company_id, user_id, role)
    values ('11111111-1111-1111-1111-111111111111', new.id, 'owner')
    on conflict (company_id, user_id) do nothing;
  end if;

  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
