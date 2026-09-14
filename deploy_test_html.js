import fs from 'fs'

const code = `
Deno.serve(async (req) => {
  return new Response('<h1>Test HTML</h1>', {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  })
})
`
fs.writeFileSync('/tmp/test-html.ts', code)
