ALTER TABLE public.payment_receipts 
ADD COLUMN IF NOT EXISTS receipt_number text,
ADD COLUMN IF NOT EXISTS contact_id uuid references public.contacts(id) on delete set null,
ADD COLUMN IF NOT EXISTS customer_name_freeform text,
ADD COLUMN IF NOT EXISTS notes text;
