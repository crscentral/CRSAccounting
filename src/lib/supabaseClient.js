import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://pxygyucscjmvgvfilohq.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_daz-WI4nSsASBYZHVNkQyA_Z4IAl7QO'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
