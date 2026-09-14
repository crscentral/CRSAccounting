-- Allow platform admins to delete any company
CREATE OR REPLACE FUNCTION is_platform_admin() RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.user_profiles
    WHERE id = auth.uid() AND is_platform_admin = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE POLICY "platform admins can delete companies" ON public.companies 
  FOR DELETE USING (is_platform_admin());

-- Allow company owners to delete their own company
CREATE POLICY "owners can delete company" ON public.companies
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.company_members
      WHERE company_id = id AND user_id = auth.uid() AND role = 'owner'
    )
  );
