import { useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import logo from '../assets/crs-logo.png'

export default function Login() {
  const [mode, setMode] = useState('signin') // 'signin' | 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError(''); setMessage(''); setLoading(true)
    try {
      if (mode === 'signin') {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
      } else {
        const { data: signUpData, error } = await supabase.auth.signUp({
          email, password,
          options: { data: { full_name: fullName } },
        })
        if (error) throw error
        if (signUpData?.session) {
          setMessage('Account created successfully!')
        } else {
          setMessage('Account created! Please sign in with your email and password to set up your company.')
          setMode('signin')
        }
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <header className="flex flex-col items-center mb-6">
          <img src={logo} alt="CRS Accounting logo" width="64" height="64" className="h-16 w-16 object-contain mb-3" />
          <h1 className="text-xl font-bold text-navy-800">CRS Accounting</h1>
          <p className="text-xs text-slate-600 mt-1">A unit of CRS Chauhan Private Limited</p>
        </header>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4" aria-label={mode === 'signin' ? 'Sign in form' : 'Create account form'}>
            {mode === 'signup' && (
              <div>
                <label htmlFor="login-fullname" className="block text-xs font-semibold text-slate-700">Full Name</label>
                <input
                  id="login-fullname"
                  name="name"
                  type="text"
                  autoComplete="name"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  required
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-navy-600"
                />
              </div>
            )}
            <div>
              <label htmlFor="login-email" className="block text-xs font-semibold text-slate-700">Email</label>
              <input
                id="login-email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-navy-600"
              />
            </div>
            <div>
              <label htmlFor="login-password" className="block text-xs font-semibold text-slate-700">Password</label>
              <input
                id="login-password"
                name="password"
                type="password"
                autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                minLength={6}
                className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-navy-600"
              />
            </div>

            {error && <p role="alert" aria-live="polite" className="text-xs text-red-700 font-medium">{error}</p>}
            {message && <p role="status" aria-live="polite" className="text-xs text-emerald-700 font-medium">{message}</p>}

            <button
              disabled={loading}
              type="submit"
              aria-busy={loading}
              className="w-full bg-navy-600 hover:bg-navy-700 text-white font-semibold rounded-lg py-2.5 text-sm disabled:opacity-60 transition-colors"
            >
              {loading ? 'Please wait…' : mode === 'signin' ? 'Log In' : 'Create Account'}
            </button>
          </form>

          <button
            type="button"
            onClick={() => { setMode(m => m === 'signin' ? 'signup' : 'signin'); setError(''); setMessage('') }}
            className="w-full text-center text-xs text-navy-700 hover:text-navy-900 hover:underline mt-4 font-semibold py-2"
          >
            {mode === 'signin' ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
          </button>
        </div>
      </div>
    </main>
  )
}
