require('@babel/register')({
  presets: [
    ['@babel/preset-react', { runtime: 'automatic' }]
  ],
  extensions: ['.jsx', '.js']
})

const React = require('react')
const ReactDOMServer = require('react-dom/server')

// Mock out imports that might fail in Node
const mockModule = new Proxy({}, { get: () => () => null })
require.cache[require.resolve('../lib/supabaseClient')] = { exports: { supabase: { from: () => ({ select: () => ({ eq: () => ({ order: () => ({ maybeSingle: () => ({}) }) }) }) }) } } }

try {
  const AppShell = require('./src/components/AppShell.jsx').default
  console.log("AppShell parsed.")
} catch (e) {
  console.error("Parse Error:", e)
}
