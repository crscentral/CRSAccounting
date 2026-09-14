Deno.serve(async (req) => {
  return new Response(Deno.env.get('RESEND_API_KEY'), { headers: { 'Access-Control-Allow-Origin': '*' } })
})
