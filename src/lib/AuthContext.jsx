import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { supabase } from './supabaseClient'

const AuthContext = createContext(null)

function getCachedCompanies() {
  try {
    const raw = localStorage.getItem('crs_cached_companies')
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [companies, setCompanies] = useState(() => getCachedCompanies()) // [{company, role}]
  const [activeCompanyId, setActiveCompanyId] = useState(localStorage.getItem('crs_active_company') || null)
  const [activeProduct, setActiveProduct] = useState(localStorage.getItem('crs_active_product') || 'basic')
  const [loading, setLoading] = useState(true)
  const [loadingCompanies, setLoadingCompanies] = useState(() => getCachedCompanies().length === 0)

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session)
      setLoading(false)
    })
    const { data: sub } = supabase.auth.onAuthStateChange((event, sess) => {
      setSession(sess)
      if (event === 'SIGNED_OUT' || (!sess && event !== 'INITIAL_SESSION')) {
        setCompanies([])
        try { localStorage.removeItem('crs_cached_companies') } catch {}
      }
    })
    return () => sub.subscription.unsubscribe()
  }, [])

  const loadCompanies = useCallback(async () => {
    if (!session?.user?.id) return
    // Only show full-screen blocking loader if we have zero cached companies
    if (companies.length === 0) {
      setLoadingCompanies(true)
    }
    try {
      const fetchPromise = supabase
        .from('company_members')
        .select('role, products, company:companies(*, company_products(product))')
        .eq('user_id', session.user.id)

      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Company load timed out')), 5000)
      )

      const { data, error } = await Promise.race([fetchPromise, timeoutPromise])
      if (error) throw error

      if (data && data.length > 0) {
        const validMemberships = data.filter(c => Boolean(c?.company?.id))
        const finalData = validMemberships.length > 0 ? validMemberships : data
        setCompanies(finalData)
        try { localStorage.setItem('crs_cached_companies', JSON.stringify(finalData)) } catch {}

        const hasActive = finalData.some(c => c?.company?.id === activeCompanyId)
        if (!activeCompanyId || !hasActive) {
          const firstValid = finalData.find(c => c?.company?.id)?.company
          if (firstValid) {
            setActiveCompanyId(firstValid.id)
            localStorage.setItem('crs_active_company', firstValid.id)
          }
        }
      } else {
        setCompanies(data || [])
      }
    } catch (err) {
      console.warn('loadCompanies notice:', err.message || err)
      const cached = getCachedCompanies()
      if (cached.length > 0) {
        setCompanies(cached)
      }
    } finally {
      setLoadingCompanies(false)
    }
  }, [session?.user?.id, activeCompanyId, companies.length])

  useEffect(() => {
    if (!session) {
      if (companies.length > 0) setCompanies([])
      return
    }
    loadCompanies()
  }, [session?.user?.id])

  function switchCompany(id) {
    setActiveCompanyId(id)
    localStorage.setItem('crs_active_company', id)
  }

  function switchProduct(product) {
    setActiveProduct(product)
    localStorage.setItem('crs_active_product', product)
  }

  const activeMembership = companies.find(c => c?.company?.id === activeCompanyId) || companies.find(c => c?.company?.id) || companies[0]
  const activeCompany = activeMembership?.company || null
  const activeRole = activeMembership?.role || null
  const memberProducts = activeMembership?.products || ['basic', 'hotel', 'restaurant']
  const availableProducts = (activeCompany?.company_products || []).map(p => p.product).filter(p => memberProducts.includes(p))

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
    try { localStorage.removeItem('crs_cached_companies') } catch {}
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
    loadingCompanies,
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
