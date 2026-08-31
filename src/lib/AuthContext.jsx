import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from './supabaseClient'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [companies, setCompanies] = useState([]) // [{company, role}]
  const [activeCompanyId, setActiveCompanyId] = useState(localStorage.getItem('crs_active_company') || null)
  const [activeProduct, setActiveProduct] = useState(localStorage.getItem('crs_active_product') || 'basic')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session)
      setLoading(false)
    })
    const { data: sub } = supabase.auth.onAuthStateChange((_event, sess) => {
      setSession(sess)
    })
    return () => sub.subscription.unsubscribe()
  }, [])

  useEffect(() => {
    if (!session) { setCompanies([]); return }
    loadCompanies()
  }, [session])

  async function loadCompanies() {
    const { data, error } = await supabase
      .from('company_members')
      .select('role, company:companies(*, company_products(product))')
      .eq('user_id', session.user.id)
    if (error) { console.error(error); return }
    setCompanies(data || [])
    if (data && data.length > 0 && !activeCompanyId) {
      setActiveCompanyId(data[0].company.id)
      localStorage.setItem('crs_active_company', data[0].company.id)
    }
  }

  function switchCompany(id) {
    setActiveCompanyId(id)
    localStorage.setItem('crs_active_company', id)
  }

  function switchProduct(product) {
    setActiveProduct(product)
    localStorage.setItem('crs_active_product', product)
  }

  const activeMembership = companies.find(c => c.company.id === activeCompanyId) || companies[0]
  const activeCompany = activeMembership?.company || null
  const activeRole = activeMembership?.role || null
  const availableProducts = (activeCompany?.company_products || []).map(p => p.product)

  // If the currently-selected product isn't actually enabled for the active company
  // (e.g. just switched companies, or an admin revoked a product), fall back to
  // whichever product IS enabled -- 'basic' if present, otherwise the first one.
  useEffect(() => {
    if (availableProducts.length === 0) return
    if (!availableProducts.includes(activeProduct)) {
      switchProduct(availableProducts.includes('basic') ? 'basic' : availableProducts[0])
    }
  }, [activeCompany?.id, availableProducts.join(',')])

  async function signOut() {
    await supabase.auth.signOut()
  }

  const value = {
    session,
    user: session?.user || null,
    companies,
    activeCompany,
    activeRole,
    switchCompany,
    activeProduct,
    availableProducts,
    switchProduct,
    signOut,
    loading,
    refreshCompanies: loadCompanies,
    can: (roles) => activeRole && roles.includes(activeRole),
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
