import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
const env = fs.readFileSync('.env', 'utf8')
const matchUrl = env.match(/VITE_SUPABASE_URL=(.*)/)
const matchKey = env.match(/VITE_SUPABASE_ANON_KEY=(.*)/)
const supabase = createClient(matchUrl[1], matchKey[1])
async function run() {
  // Try to insert a dummy row into a non-existent table to get the schema of hotel_room_stats? No, just select 1 row.
  const { data, error } = await supabase.from('hotel_room_stats').select('*').limit(1)
  console.log("Stats:", data, error)
  const { data: d2, error: e2 } = await supabase.from('hotel_guest_invoices').select('*').limit(1)
  console.log("Invoices:", d2, e2)
}
run()
