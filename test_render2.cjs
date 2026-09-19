require('@babel/register')({
  presets: [['@babel/preset-react', { runtime: 'automatic' }]],
  extensions: ['.jsx', '.js']
})

const React = require('react')
const ReactDOMServer = require('react-dom/server')
const App = require('./src/App.jsx').default

// Mock dependencies
require.cache[require.resolve('./src/lib/supabaseClient')] = { exports: { supabase: {} } }

try {
  const HotelExpenseBudget = require('./src/pages/HotelExpenseBudget.jsx').default
  console.log("HotelExpenseBudget parsed successfully")
} catch (e) {
  console.error("FATAL ERROR IN COMPONENT:", e)
}
