-- Add invoice_number to hotel_guest_invoices
ALTER TABLE hotel_guest_invoices ADD COLUMN IF NOT EXISTS invoice_number text;
