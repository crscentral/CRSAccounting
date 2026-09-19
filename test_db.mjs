import { supabase } from './src/lib/supabaseClient.js'

async function check() {
  const { data, error } = await supabase.from('hotel_revenue_budget').select('id').limit(1)
  console.log("hotel_revenue_budget:", error ? error.message : "EXISTS")
}
check()
