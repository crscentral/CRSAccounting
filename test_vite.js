import { loadEnv } from 'vite'
import { createClient } from '@supabase/supabase-js'

const env = loadEnv('development', process.cwd(), '')
const supabase = createClient(env.VITE_SUPABASE_URL, env.VITE_SUPABASE_ANON_KEY)

supabase.from('hotel_guest_invoices').select('invoice_number').limit(1).then(r => console.log(r))
