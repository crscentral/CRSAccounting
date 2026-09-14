import { execSync } from 'child_process'
import fs from 'fs'

const code = `import { createClient } from 'jsr:@supabase/supabase-js@2'

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type' } })
  }

  const apiKey = Deno.env.get('RESEND_API_KEY')
  
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: \`Bearer \${apiKey}\`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: 'CRS Accounting <onboarding@resend.dev>',
      to: ['crscentral.rm@gmail.com'],
      subject: 'Test API key',
      html: '<p>Testing</p>'
    })
  })
  
  return new Response(await res.text(), { status: res.ok ? 200 : 500, headers: { 'Access-Control-Allow-Origin': '*' } })
})
`
fs.writeFileSync('/tmp/test-fn.ts', code)
