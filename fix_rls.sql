CREATE POLICY "platform admin sees all members" ON public.company_members FOR SELECT USING (
  public.is_platform_admin()
);

CREATE POLICY "platform admin sees all profiles" ON public.user_profiles FOR SELECT USING (
  public.is_platform_admin()
);

ALTER TABLE public.company_members ADD CONSTRAINT company_members_user_profile_fkey FOREIGN KEY (user_id) REFERENCES public.user_profiles(id) ON DELETE CASCADE;
