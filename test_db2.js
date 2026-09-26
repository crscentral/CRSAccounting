import { createClient } from '@supabase/supabase-js'
import fs from 'fs'

const envStr = fs.readFileSync('.env.local', 'utf8')
const env = {}
envStr.split('\n').forEach(l => {
  if (l.includes('=')) {
    const [k,v] = l.split('=')
    env[k] = v.trim()
  }
})

const supabase = createClient(env.VITE_SUPABASE_URL, env.VITE_SUPABASE_ANON_KEY)
supabase.from('hotel_guest_invoices').select('*').limit(1).then(r => console.log(r.error ? r.error : Object.keys(r.data[0] || {})))
