import { createClient } from 'jsr:@supabase/supabase-js@2'

const ADMIN_TO = 'crscentral.rm@gmail.com'
const ADMIN_CC = 'info@crscentral.com'
const FUNCTIONS_BASE = 'https://pxygyucscjmvgvfilohq.supabase.co/functions/v1'

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      },
    })
  }

  try {
    const { companyId, companyName, signupEmail, ownerFullName } = await req.json()

    const apiKey = Deno.env.get('RESEND_API_KEY')
    if (!apiKey) {
      return new Response(JSON.stringify({ error: 'RESEND_API_KEY not configured' }), { status: 500 })
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    let company = null
    if (companyId) {
      const { data, error } = await supabase.from('companies').select('*').eq('id', companyId).single()
      if (!error && data) company = data
    }

    const cId = company?.id || companyId
    const cName = company?.name || companyName || 'New Company'
    const token = company?.approval_token || ''
    const currency = company?.base_currency || 'USD'

    const reviewUrl = `${FUNCTIONS_BASE}/approve-company-page?company_id=${cId}&token=${token}`

    // Instead of onboarding@resend.dev, try info@crscentral.com in case the domain is verified!
    // Or we try onboarding@resend.dev. If it fails, we fall back? No, let's just use info@crscentral.com.
    
    let res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: 'CRS Accounting <info@crscentral.com>',
        to: [ADMIN_TO],
        cc: [ADMIN_CC],
        subject: `[CRS Accounting] Approval needed: New company "${cName}"`,
        html: `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
            <h2 style="color: #1B3A6B; margin-top: 0;">New Company Sign-up Approval Required</h2>
            <p style="color: #475569; font-size: 15px;">A new user has signed up for CRS Accounting and created a company requiring your approval:</p>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin: 16px 0;">
              <p style="margin: 4px 0; color: #334155;"><strong>Company Name:</strong> ${cName}</p>
              <p style="margin: 4px 0; color: #334155;"><strong>Applicant Name:</strong> ${ownerFullName || 'N/A'}</p>
              <p style="margin: 4px 0; color: #334155;"><strong>Applicant Email:</strong> ${signupEmail}</p>
              <p style="margin: 4px 0; color: #334155;"><strong>Base Currency:</strong> ${currency}</p>
            </div>
            <p style="margin: 24px 0;">
              <a href="${reviewUrl}" style="background: #1B3A6B; color: #ffffff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block;">Review &amp; Approve</a>
            </p>
          </div>
        `
      })
    })

    let resData = await res.text()
    
    // If info@crscentral.com fails because the domain isn't verified, fall back to onboarding@resend.dev
    if (!res.ok) {
      console.log('Failed with info@crscentral.com, falling back to onboarding@resend.dev')
      res = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from: 'CRS Accounting <onboarding@resend.dev>',
          to: [ADMIN_TO],
          cc: [ADMIN_CC],
          subject: `[CRS Accounting] Approval needed: New company "${cName}"`,
          html: `<p>A new user has signed up and created a company requiring your approval. <a href="${reviewUrl}">Review & Approve</a></p>`
        })
      })
      resData = await res.text()
    }

    if (!res.ok) {
      return new Response(JSON.stringify({ error: resData }), { status: 500, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } })
    }

    return new Response(JSON.stringify({ ok: true, data: resData }), { status: 200, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } })
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), { status: 500, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } })
  }
})
