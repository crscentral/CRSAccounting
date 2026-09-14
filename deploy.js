import fs from 'fs'

const code = fs.readFileSync('/Users/sumantsingh/.gemini/antigravity/brain/a101a607-397b-4a80-b151-c0b335335fd5/scratch/CRSAccounting/patch_notify_company.ts', 'utf8')

fetch('https://api.supabase.com/v1/projects/pxygyucscjmvgvfilohq/functions/notify-pending-company', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${process.env.SUPABASE_ACCESS_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'notify-pending-company',
    files: [{ name: 'index.ts', content: code }]
  })
}).then(res => res.json()).then(console.log).catch(console.error)
