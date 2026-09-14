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
    const { invitedEmail, inviterName, companyName, role } = await req.json()

    const apiKey = Deno.env.get('RESEND_API_KEY')
    if (!apiKey) {
      return new Response(JSON.stringify({ error: 'RESEND_API_KEY not configured in Supabase' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      })
    }

    const signupUrl = 'https://crscentral.github.io/CRSAccounting/login'
    const htmlContent = `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
            <h2 style="color: #1B3A6B; margin-top: 0;">You are invited to CRS Accounting</h2>
            <p style="color: #475569; font-size: 15px;">
              <strong>${inviterName || 'Your team admin'}</strong> has invited you to join
              <strong>${companyName}</strong> on CRS Accounting as a <strong>${role}</strong>.
            </p>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin: 16px 0;">
              <p style="margin: 4px 0; color: #334155;"><strong>Invited email:</strong> ${invitedEmail}</p>
              <p style="margin: 4px 0; color: #334155;"><strong>Company:</strong> ${companyName}</p>
              <p style="margin: 4px 0; color: #334155;"><strong>Role:</strong> ${role}</p>
            </div>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
              To accept this invitation, simply <strong>sign up or log in</strong> using <strong>${invitedEmail}</strong>.
              Your access to <strong>${companyName}</strong> will be granted automatically.
            </p>
            <p style="margin: 28px 0;">
              <a href="${signupUrl}" style="background: #1B3A6B; color: #ffffff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block;">Sign Up / Log In to CRS Accounting</a>
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
        to: [invitedEmail],
        subject: `You have been invited to join ${companyName} on CRS Accounting`,
        html: htmlContent
      }),
    })

    let resData = await res.text()
    if (!res.ok) {
        res = await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            from: 'CRS Accounting <onboarding@resend.dev>',
            to: [invitedEmail],
            subject: `You have been invited to join ${companyName} on CRS Accounting`,
            html: htmlContent
          }),
        })
        resData = await res.text()
    }

    if (!res.ok) {
      return new Response(JSON.stringify({ error: resData }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      })
    }

    return new Response(JSON.stringify({ ok: true, data: resData }), {
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
