import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.VITE_SUPABASE_URL,
  process.env.VITE_SUPABASE_SERVICE_ROLE_KEY // using service role to see what it returns
)

async function test() {
  const { data, error } = await supabase
      .from('companies')
      .select('*, members:company_members(role, user_id, profile:user_profiles(email, full_name))')
      .eq('approval_status', 'pending')
      .order('created_at', { ascending: false })
      
  console.log(data)
  console.log("Error:", error)
}
test()
