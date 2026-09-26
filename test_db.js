import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_ANON_KEY)
supabase.from('hotel_guest_invoices').select('invoice_number').limit(1).then(r => console.log(r))
