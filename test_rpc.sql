CREATE OR REPLACE FUNCTION test_pending() RETURNS json AS $$
DECLARE
  res json;
BEGIN
  -- set local role to authenticated
  SET LOCAL role = authenticated;
  -- mock jwt
  SET LOCAL request.jwt.claim.email = 'crscentral.rm@gmail.com';
  
  SELECT json_agg(t) INTO res FROM (
    SELECT * FROM companies WHERE approval_status = 'pending'
  ) t;
  
  RETURN res;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
