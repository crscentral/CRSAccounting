require('dotenv').config({ path: '.env' })
const { createClient } = require('@supabase/supabase-js')
const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_ANON_KEY)

async function test() {
  const companyId = '43d853ee-a438-4485-ba53-2def720e0a3e'
  const product = 'hotel'
  const range = { from: '2026-01-01', to: '2026-12-31' }
  try {
      const [{ data: hrs }, { data: hre }, { data: rdr }, { data: hee }, { data: amc }, { data: hgi }, { data: pur }] = await Promise.all([
        supabase.from('hotel_room_stats').select('*').eq('company_id', companyId).eq('product', product).gte('stat_date', range.from).lte('stat_date', range.to),
        supabase.from('hotel_revenue_entries').select('*').eq('company_id', companyId).eq('product', product).gte('entry_date', range.from).lte('entry_date', range.to),
        supabase.from('restaurant_daily_revenue').select('*').eq('company_id', companyId).eq('product', product).gte('revenue_date', range.from).lte('revenue_date', range.to),
        supabase.from('hotel_expense_entries').select('*').eq('company_id', companyId).eq('product', product).gte('expense_date', range.from).lte('expense_date', range.to),
        supabase.from('hotel_amc_contracts').select('*').eq('company_id', companyId).eq('product', product),
        supabase.from('hotel_guest_invoices').select('*').eq('company_id', companyId).eq('product', product).gte('invoice_date', range.from).lte('invoice_date', range.to),
        supabase.from('purchase_invoices').select('*').eq('company_id', companyId).eq('product', product).gte('invoice_date', range.from).lte('invoice_date', range.to)
      ])
      console.log("Success")
  } catch(e) {
      console.log("ERROR", e)
  }
}
test()
