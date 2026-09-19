const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('http://localhost:54321', 'test', { auth: { persistSession: false } }) // Just need a stub, or actually I should use their env vars!
