CREATE OR REPLACE FUNCTION set_company_products(p_company_id UUID, p_products TEXT[])
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Only allow platform admin
  IF auth.jwt()->>'email' != 'crscentral.rm@gmail.com' THEN
    RAISE EXCEPTION 'Not authorized';
  END IF;

  DELETE FROM company_products WHERE company_id = p_company_id;
  
  IF array_length(p_products, 1) > 0 THEN
    INSERT INTO company_products (company_id, product)
    SELECT p_company_id, unnest(p_products);
  END IF;
END;
$$;
