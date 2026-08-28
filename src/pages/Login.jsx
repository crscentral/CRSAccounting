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
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-6">
          <img src={logo} alt="CRS Accounting" className="h-16 w-16 object-contain mb-3" />
          <h1 className="text-xl font-bold text-navy-700">CRS Accounting</h1>
          <p className="text-xs text-slate-400 mt-1">A unit of CRS Chauhan Private Limited</p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'signup' && (
              <div>
                <label className="text-xs font-medium text-slate-500">Full Name</label>
                <input value={fullName} onChange={e => setFullName(e.target.value)} required
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
              </div>
            )}
            <div>
              <label className="text-xs font-medium text-slate-500">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
                className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-500">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={6}
                className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>

            {error && <p className="text-xs text-red-600">{error}</p>}
            {message && <p className="text-xs text-emerald-600">{message}</p>}

            <button disabled={loading} type="submit"
              className="w-full bg-navy-600 hover:bg-navy-700 text-white font-medium rounded-lg py-2.5 text-sm disabled:opacity-60">
              {loading ? 'Please wait…' : mode === 'signin' ? 'Log In' : 'Create Account'}
            </button>
          </form>

          <button
            onClick={() => { setMode(m => m === 'signin' ? 'signup' : 'signin'); setError(''); setMessage('') }}
            className="w-full text-center text-xs text-navy-600 mt-4"
          >
            {mode === 'signin' ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
          </button>
        </div>
      </div>
    </div>
  )
}
