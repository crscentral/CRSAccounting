CREATE TABLE IF NOT EXISTS public.owner_contributions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  company_id uuid NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  product public.product_type NOT NULL,
  owner_name text NOT NULL,
  payment_date date NOT NULL,
  currency text NOT NULL,
  fx_rate_locked numeric NOT NULL,
  amount numeric NOT NULL,
  amount_usd numeric NOT NULL,
  notes text
);

ALTER TABLE public.owner_contributions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all for authenticated users on owner_contributions"
  ON public.owner_contributions FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE OR REPLACE FUNCTION post_owner_contribution_to_ledger()
RETURNS trigger AS $$
DECLARE 
  oc_id uuid; 
  cash_id uuid;
BEGIN
  -- 3010 Owner's Contribution
  SELECT id INTO oc_id FROM public.accounts WHERE company_id = NEW.company_id AND product = NEW.product AND code = '3010' LIMIT 1;
  -- 1010 Cash on Hand
  SELECT id INTO cash_id FROM public.accounts WHERE company_id = NEW.company_id AND product = NEW.product AND code = '1010' LIMIT 1;
  
  IF cash_id IS NOT NULL THEN
    INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
    VALUES (NEW.company_id, NEW.product, cash_id, NEW.payment_date, 'Owner Contribution - ' || NEW.owner_name, NEW.currency, NEW.fx_rate_locked, NEW.amount_usd, 0, 'owner_contribution', NEW.id);
  END IF;

  IF oc_id IS NOT NULL THEN
    INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
    VALUES (NEW.company_id, NEW.product, oc_id, NEW.payment_date, 'Owner Contribution - ' || NEW.owner_name, NEW.currency, NEW.fx_rate_locked, 0, NEW.amount_usd, 'owner_contribution', NEW.id);
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_post_owner_contribution
  AFTER INSERT ON public.owner_contributions
  FOR EACH ROW EXECUTE FUNCTION post_owner_contribution_to_ledger();

CREATE OR REPLACE FUNCTION delete_owner_contribution_ledger_entries()
RETURNS trigger AS $$
BEGIN
  DELETE FROM public.ledger_entries WHERE source_type = 'owner_contribution' AND source_id = OLD.id;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_delete_owner_contribution_ledger
  BEFORE DELETE ON public.owner_contributions
  FOR EACH ROW EXECUTE FUNCTION delete_owner_contribution_ledger_entries();

-- LOANS TAKEN --

CREATE TABLE IF NOT EXISTS public.loans_taken (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  company_id uuid NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  product public.product_type NOT NULL,
  loan_account_id uuid NOT NULL REFERENCES public.accounts(id) ON DELETE CASCADE,
  cash_account_id uuid NOT NULL REFERENCES public.accounts(id) ON DELETE CASCADE,
  payment_date date NOT NULL,
  currency text NOT NULL,
  fx_rate_locked numeric NOT NULL,
  amount numeric NOT NULL,
  amount_usd numeric NOT NULL,
  notes text
);

ALTER TABLE public.loans_taken ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all for authenticated users on loans_taken"
  ON public.loans_taken FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE OR REPLACE FUNCTION post_loan_taken_to_ledger()
RETURNS trigger AS $$
BEGIN
  -- Debit Cash (Asset increases)
  INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
  VALUES (NEW.company_id, NEW.product, NEW.cash_account_id, NEW.payment_date, 'Loan Taken', NEW.currency, NEW.fx_rate_locked, NEW.amount_usd, 0, 'loan_taken', NEW.id);
  
  -- Credit Loan (Liability increases)
  INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
  VALUES (NEW.company_id, NEW.product, NEW.loan_account_id, NEW.payment_date, 'Loan Taken', NEW.currency, NEW.fx_rate_locked, 0, NEW.amount_usd, 'loan_taken', NEW.id);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_post_loan_taken
  AFTER INSERT ON public.loans_taken
  FOR EACH ROW EXECUTE FUNCTION post_loan_taken_to_ledger();

CREATE OR REPLACE FUNCTION delete_loan_taken_ledger_entries()
RETURNS trigger AS $$
BEGIN
  DELETE FROM public.ledger_entries WHERE source_type = 'loan_taken' AND source_id = OLD.id;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_delete_loan_taken_ledger
  BEFORE DELETE ON public.loans_taken
  FOR EACH ROW EXECUTE FUNCTION delete_loan_taken_ledger_entries();

