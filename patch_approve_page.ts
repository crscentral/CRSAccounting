import { createClient } from 'jsr:@supabase/supabase-js@2'

const SUBMIT_URL = 'https://pxygyucscjmvgvfilohq.supabase.co/functions/v1/approve-company-submit'

function page(body: string) {
  return new Response(
    `<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family:sans-serif;max-width:420px;margin:60px auto;padding:0 20px;color:#1B3A6B;">
      ${body}
    </body></html>`,
    { 
      status: 200,
      headers: new Headers({
        'Content-Type': 'text/html; charset=utf-8',
        'Access-Control-Allow-Origin': '*'
      }) 
    }
  )
}

Deno.serve(async (req) => {
  const url = new URL(req.url)
  const companyId = url.searchParams.get('company_id')
  const token = url.searchParams.get('token')

  if (!companyId || !token) return page('<h2>Invalid link</h2><p>This approval link is malformed.</p>')

  const supabase = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!)
  const { data: company, error } = await supabase.from('companies').select('id, name, approval_status, approval_token').eq('id', companyId).single()

  if (error || !company) return page('<h2>Not found</h2><p>This company could not be found.</p>')
  if (company.approval_token !== token) return page('<h2>Link already used</h2><p>This approval link is invalid or has already been used.</p>')
  if (company.approval_status !== 'pending') return page(`<h2>Already handled</h2><p><strong>${company.name}</strong> has already been ${company.approval_status}.</p>`)

  return page(`
    <h2>Review Sign-up</h2>
    <p><strong>${company.name}</strong> is waiting for approval.</p>
    <form method="POST" action="${SUBMIT_URL}">
      <input type="hidden" name="company_id" value="${company.id}" />
      <input type="hidden" name="token" value="${token}" />
      <p style="font-weight:bold;margin-bottom:8px;">Grant access to:</p>
      <label style="display:block;margin-bottom:6px;"><input type="checkbox" name="products" value="basic" checked /> CRS Basic Accounting</label>
      <label style="display:block;margin-bottom:6px;"><input type="checkbox" name="products" value="hotel" /> CRS Hotel Accounting</label>
      <label style="display:block;margin-bottom:16px;"><input type="checkbox" name="products" value="restaurant" /> CRS Restaurant Accounting</label>
      <button type="submit" name="action" value="approve" style="background:#16a34a;color:#fff;padding:10px 20px;border:none;border-radius:6px;font-weight:bold;margin-right:10px;cursor:pointer;">Approve</button>
      <button type="submit" name="action" value="reject" style="background:#dc2626;color:#fff;padding:10px 20px;border:none;border-radius:6px;font-weight:bold;cursor:pointer;">Reject</button>
    </form>
  `)
})
