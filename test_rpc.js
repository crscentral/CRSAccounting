import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://pxygyucscjmvgvfilohq.supabase.co',
  'sb_publishable_daz-WI4nSsASBYZHVNkQyA_Z4IAl7QO' // from src/lib/supabaseClient.js
)

async function testRPC() {
  const { data, error } = await supabase.rpc('exec_sql', { sql_string: 'SELECT 1' })
  if (error) {
    console.log("exec_sql failed:", error.message)
    const res2 = await supabase.rpc('run_sql', { query: 'SELECT 1' })
    if (res2.error) console.log("run_sql failed:", res2.error.message)
    else console.log("run_sql success:", res2.data)
  } else {
    console.log("exec_sql success:", data)
  }
}
testRPC()
