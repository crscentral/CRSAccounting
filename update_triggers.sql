-- Owner Dividends Update
CREATE OR REPLACE FUNCTION update_owner_dividend_ledger_entries() RETURNS trigger AS $$
BEGIN
  DELETE FROM public.ledger_entries WHERE source_type = 'owner_dividend' AND source_id = OLD.id;
  
  DECLARE 
    re_id uuid; 
    cash_id uuid;
  BEGIN
    SELECT id INTO re_id FROM public.accounts WHERE company_id = NEW.company_id AND product = NEW.product AND code = '3020' LIMIT 1;
    SELECT id INTO cash_id FROM public.accounts WHERE company_id = NEW.company_id AND product = NEW.product AND code = '1010' LIMIT 1;
    
    IF re_id IS NOT NULL THEN
      INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
      VALUES (NEW.company_id, NEW.product, re_id, NEW.payment_date, 'Owner Dividend - ' || NEW.owner_name, NEW.currency, NEW.fx_rate_locked, NEW.amount_usd, 0, 'owner_dividend', NEW.id);
    END IF;
    IF cash_id IS NOT NULL THEN
      INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
      VALUES (NEW.company_id, NEW.product, cash_id, NEW.payment_date, 'Owner Dividend - ' || NEW.owner_name, NEW.currency, NEW.fx_rate_locked, 0, NEW.amount_usd, 'owner_dividend', NEW.id);
    END IF;
  END;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_update_owner_dividend AFTER UPDATE ON public.owner_dividends FOR EACH ROW EXECUTE FUNCTION update_owner_dividend_ledger_entries();

-- Loan Principal Update
CREATE OR REPLACE FUNCTION update_loan_principal_ledger_entries() RETURNS trigger AS $$
BEGIN
  DELETE FROM public.ledger_entries WHERE source_type = 'loan_principal_payment' AND source_id = OLD.id;
  
  INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
  VALUES (NEW.company_id, NEW.product, NEW.loan_account_id, NEW.payment_date, 'Loan Principal Repayment', NEW.currency, NEW.fx_rate_locked, NEW.amount_usd, 0, 'loan_principal_payment', NEW.id);
  INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
  VALUES (NEW.company_id, NEW.product, NEW.cash_account_id, NEW.payment_date, 'Loan Principal Repayment', NEW.currency, NEW.fx_rate_locked, 0, NEW.amount_usd, 'loan_principal_payment', NEW.id);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_update_loan_principal AFTER UPDATE ON public.loan_principal_payments FOR EACH ROW EXECUTE FUNCTION update_loan_principal_ledger_entries();

-- Owner Contributions Update
CREATE OR REPLACE FUNCTION update_owner_contribution_ledger_entries() RETURNS trigger AS $$
BEGIN
  DELETE FROM public.ledger_entries WHERE source_type = 'owner_contribution' AND source_id = OLD.id;
  
  DECLARE 
    oc_id uuid; 
    cash_id uuid;
  BEGIN
    SELECT id INTO oc_id FROM public.accounts WHERE company_id = NEW.company_id AND product = NEW.product AND code = '3010' LIMIT 1;
    SELECT id INTO cash_id FROM public.accounts WHERE company_id = NEW.company_id AND product = NEW.product AND code = '1010' LIMIT 1;
    
    IF cash_id IS NOT NULL THEN
      INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
      VALUES (NEW.company_id, NEW.product, cash_id, NEW.payment_date, 'Owner Contribution - ' || NEW.owner_name, NEW.currency, NEW.fx_rate_locked, NEW.amount_usd, 0, 'owner_contribution', NEW.id);
    END IF;
    IF oc_id IS NOT NULL THEN
      INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
      VALUES (NEW.company_id, NEW.product, oc_id, NEW.payment_date, 'Owner Contribution - ' || NEW.owner_name, NEW.currency, NEW.fx_rate_locked, 0, NEW.amount_usd, 'owner_contribution', NEW.id);
    END IF;
  END;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_update_owner_contribution AFTER UPDATE ON public.owner_contributions FOR EACH ROW EXECUTE FUNCTION update_owner_contribution_ledger_entries();

-- Loans Taken Update
CREATE OR REPLACE FUNCTION update_loan_taken_ledger_entries() RETURNS trigger AS $$
BEGIN
  DELETE FROM public.ledger_entries WHERE source_type = 'loan_taken' AND source_id = OLD.id;
  
  INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
  VALUES (NEW.company_id, NEW.product, NEW.cash_account_id, NEW.payment_date, 'Loan Taken', NEW.currency, NEW.fx_rate_locked, NEW.amount_usd, 0, 'loan_taken', NEW.id);
  INSERT INTO public.ledger_entries (company_id, product, account_id, entry_date, description, currency, fx_rate_locked, debit_usd, credit_usd, source_type, source_id)
  VALUES (NEW.company_id, NEW.product, NEW.loan_account_id, NEW.payment_date, 'Loan Taken', NEW.currency, NEW.fx_rate_locked, 0, NEW.amount_usd, 'loan_taken', NEW.id);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_update_loan_taken AFTER UPDATE ON public.loans_taken FOR EACH ROW EXECUTE FUNCTION update_loan_taken_ledger_entries();
