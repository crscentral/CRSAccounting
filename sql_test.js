import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)
// wait, I can't run this without credentials.
// Let's just grep the definition of `create_company_with_owner` in the local sql files.
