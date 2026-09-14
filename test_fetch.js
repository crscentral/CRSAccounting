async function run() {
  const res = await fetch(
    `${process.env.VITE_SUPABASE_URL}/rest/v1/companies?select=*,members:company_members(role,user_id,profile:user_profiles(email,full_name))&approval_status=eq.pending&order=created_at.desc`,
    {
      headers: {
        'apikey': process.env.VITE_SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${process.env.TEST_JWT}`
      }
    }
  )
  console.log(res.status)
  console.log(await res.text())
}
run()
