import { createClient } from 'jsr:@supabase/supabase-js@2'

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
    const { companyId, applicantEmail, companyName, action } = await req.json()

    const apiKey = Deno.env.get('RESEND_API_KEY')
    if (!apiKey) {
      return new Response(JSON.stringify({ error: 'RESEND_API_KEY not configured in Supabase' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      })
    }

    if (action === 'approve' && applicantEmail) {
      const htmlContent = `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
              <h2 style="color: #1B3A6B; margin-top: 0;">Welcome to CRS Accounting!</h2>
              <p style="color: #334155; font-size: 16px; font-weight: 600;">
                Your Sign-up Request has been approved, enjoy CRS Accounting.
              </p>
              <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                Your company <strong>${companyName || 'account'}</strong> is now active. Sign in to manage accounts, create invoices, view reports, and invite your team.
              </p>
              <p style="margin: 28px 0;">
                <a href="https://crscentral.github.io/CRSAccounting/login" style="background: #1B3A6B; color: #ffffff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block;">Log In to CRS Accounting</a>
              </p>
              <p style="color: #94a3b8; font-size: 12px; border-top: 1px solid #e2e8f0; padding-top: 12px;">
                CRS Accounting &mdash; A unit of CRS Chauhan Private Limited
              </p>
            </div>
          `

      let res = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from: 'CRS Accounting <info@crscentral.com>',
          to: [applicantEmail],
          subject: 'Your CRS Accounting Sign-up Request has been approved',
          html: htmlContent
        }),
      })

      let body = await res.text()
      if (!res.ok) {
        // Fallback to resend.dev just in case
        res = await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              from: 'CRS Accounting <onboarding@resend.dev>',
              to: [applicantEmail],
              subject: 'Your CRS Accounting Sign-up Request has been approved',
              html: htmlContent
            }),
        })
        body = await res.text()
      }

      if (!res.ok) {
        return new Response(JSON.stringify({ error: body }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        })
      }
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    })
  }
})
