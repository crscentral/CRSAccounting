import { createClient } from '@supabase/supabase-js'
import fs from 'fs'

const envStr = fs.readFileSync('.env', 'utf8')
const env = {}
envStr.split('\n').forEach(l => {
  if (l.includes('=')) {
    const [k,v] = l.split('=')
    env[k] = v.trim()
  }
})

const supabase = createClient(env.VITE_SUPABASE_URL, env.VITE_SUPABASE_ANON_KEY)
supabase.from('ledger_entries').select('debit_usd, credit_usd, accounts!inner(type)').limit(1).then(r => console.log(JSON.stringify(r)))
