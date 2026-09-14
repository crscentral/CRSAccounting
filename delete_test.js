import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.VITE_SUPABASE_URL,
  process.env.VITE_SUPABASE_ANON_KEY
)
// Wait, anon key cannot delete companies directly unless RLS allows it.
// The frontend uses anon key with a logged-in user session.
// So I can't test it from the script easily without the JWT.
