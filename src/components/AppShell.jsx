import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Building2, PieChart, Users, FileCheck, FileText,
  ArrowLeftRight, BookText, TrendingUp, BarChart3, FileBarChart, Settings,
  Menu, X, LogOut, ChevronDown, Download, Share, Layers, UtensilsCrossed, Landmark, Scale, Upload, LayoutGrid,
} from 'lucide-react'
import { useAuth } from '../lib/AuthContext'
import { useInstallPrompt } from '../lib/useInstallPrompt'
import logo from '../assets/crs-logo.png'

const NAV_ITEMS = [
  { to: '/overview', label: 'All Companies', icon: LayoutGrid },
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/companies', label: 'Companies', icon: Building2 },
  { to: '/accounts', label: 'Chart of Accounts', icon: PieChart },
  { to: '/contacts', label: 'Customers & Suppliers', icon: Users },
  { to: '/sales-invoices', label: 'Sales Invoices', icon: FileCheck },
  { to: '/purchase-invoices', label: 'Purchase Invoices', icon: FileText },
  { to: '/restaurant-revenue', label: 'Table Revenue', icon: UtensilsCrossed, products: ['restaurant'] },
  { to: '/transactions', label: 'Transactions', icon: ArrowLeftRight },
  { to: '/ledger', label: 'Ledger', icon: BookText },
  { to: '/analytics', label: 'Analytics', icon: TrendingUp },
  { to: '/financial-performance', label: 'Financial Performance', icon: BarChart3 },
  { to: '/reports', label: 'Reports', icon: FileBarChart },
  { to: '/capital', label: 'Capital & Loans', icon: Landmark },
  { to: '/compare', label: 'Compare Periods', icon: Scale },
  { to: '/import', label: 'Import Data', icon: Upload },
  { to: '/settings', label: 'Settings', icon: Settings },
]

// Bottom tab bar shows only the most-used items on phones; rest live in the drawer.
const MOBILE_TAB_ITEMS = ['/', '/sales-invoices', '/purchase-invoices', '/analytics']

const PRODUCT_LABELS = { basic: 'CRS Basic Accounting', hotel: 'CRS Hotel Accounting', restaurant: 'CRS Restaurant Accounting' }

export default function AppShell() {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [installBannerDismissed, setInstallBannerDismissed] = useState(
    () => localStorage.getItem('crs_install_banner_dismissed') === '1'
  )
  const { companies, activeCompany, switchCompany, signOut, activeRole, activeProduct, availableProducts, switchProduct } = useAuth()
  const { canInstall, isStandalone, promptInstall } = useInstallPrompt()
  const navigate = useNavigate()
  const visibleNavItems = NAV_ITEMS.filter(item => !item.products || item.products.includes(activeProduct))

  const isIOS = /iphone|ipad|ipod/i.test(window.navigator.userAgent)
  const showInstallBanner = !installBannerDismissed && !isStandalone && (canInstall || isIOS)

  function dismissInstallBanner() {
    setInstallBannerDismissed(true)
    localStorage.setItem('crs_install_banner_dismissed', '1')
  }

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Desktop / tablet sidebar */}
      <aside className="hidden md:flex md:flex-col w-20 lg:w-64 border-r border-slate-200 bg-white shrink-0">
        <div className="h-16 flex items-center gap-2 px-3 lg:px-5 border-b border-slate-100">
          <img src={logo} alt="CRS Accounting" className="h-8 w-8 object-contain shrink-0" />
          <span className="hidden lg:block font-semibold text-navy-700 leading-tight">
            CRS Accounting
          </span>
        </div>

        <CompanySwitcherBlock
          companies={companies} activeCompany={activeCompany} switchCompany={switchCompany}
          collapsedLabelOnly
        />

        <nav className="flex-1 overflow-y-auto py-2">
          {visibleNavItems.map(item => (
            <NavItem key={item.to} {...item} />
          ))}
        </nav>

        <button
          onClick={signOut}
          className="flex items-center gap-3 px-3 lg:px-5 py-3 text-sm text-slate-500 hover:text-red-600 border-t border-slate-100"
        >
          <LogOut size={18} />
          <span className="hidden lg:inline">Log Out</span>
        </button>
      </aside>

      {/* Mobile drawer overlay */}
      {drawerOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setDrawerOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-72 bg-white shadow-xl flex flex-col">
            <div className="h-16 flex items-center justify-between px-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <img src={logo} alt="CRS Accounting" className="h-8 w-8 object-contain" />
                <span className="font-semibold text-navy-700">CRS Accounting</span>
              </div>
              <button onClick={() => setDrawerOpen(false)}><X size={22} /></button>
            </div>
            <CompanySwitcherBlock companies={companies} activeCompany={activeCompany} switchCompany={switchCompany} alwaysShowLabel />
            {availableProducts.length > 1 && (
              <div className="px-3 lg:px-4 py-3 border-b border-slate-100">
                <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1.5">Product</div>
                <div className="space-y-1">
                  {availableProducts.map(product => (
                    <button
                      key={product}
                      onClick={() => switchProduct(product)}
                      className={`w-full text-left px-2.5 py-1.5 rounded-lg text-sm ${product === activeProduct ? 'bg-navy-600 text-white' : 'text-slate-600 hover:bg-slate-100'}`}
                    >
                      {PRODUCT_LABELS[product]}
                    </button>
                  ))}
                </div>
              </div>
            )}
            <nav className="flex-1 overflow-y-auto py-2" onClick={() => setDrawerOpen(false)}>
              {visibleNavItems.map(item => <NavItem key={item.to} {...item} alwaysShowLabel />)}
            </nav>
            <button onClick={signOut} className="flex items-center gap-3 px-5 py-4 text-sm text-slate-500 border-t border-slate-100">
              <LogOut size={18} /> Log Out
            </button>
          </div>
        </div>
      )}

      {/* Main content column */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile top bar */}
        <header className="md:hidden h-14 bg-white border-b border-slate-200 flex items-center justify-between px-4 sticky top-0 z-30">
          <button onClick={() => setDrawerOpen(true)}><Menu size={22} className="text-navy-700" /></button>
          <div className="flex flex-col items-center">
            <div className="flex items-center gap-2">
              <img src={logo} alt="" className="h-6 w-6 object-contain" />
              <span className="font-semibold text-navy-700 text-sm">{activeCompany?.name || 'CRS Accounting'}</span>
            </div>
            {availableProducts.length > 0 && (
              <span className="text-[10px] text-slate-400 -mt-0.5">{PRODUCT_LABELS[activeProduct]}</span>
            )}
          </div>
          <div className="w-6" />
        </header>

        {/* Persistent "you are here" bar — visible on every page, every screen size */}
        <ActiveCompanyBar companies={companies} activeCompany={activeCompany} switchCompany={switchCompany} activeRole={activeRole} activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />

        {showInstallBanner && (
          <InstallBanner isIOS={isIOS} canInstall={canInstall} onInstall={promptInstall} onDismiss={dismissInstallBanner} />
        )}

        <main className="flex-1 p-3 sm:p-4 md:p-6 lg:p-8 pb-20 md:pb-8 max-w-[1600px] w-full mx-auto">
          <Outlet />
        </main>
      </div>

      {/* Mobile bottom tab bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 flex justify-around py-1.5 z-30">
        {visibleNavItems.filter(i => MOBILE_TAB_ITEMS.includes(i.to)).map(item => (
          <NavLink
            key={item.to} to={item.to} end={item.end}
            className={({ isActive }) => `flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-lg text-[11px] ${isActive ? 'text-navy-600' : 'text-slate-400'}`}
          >
            <item.icon size={20} />
            <span>{item.label.split(' ')[0]}</span>
          </NavLink>
        ))}
        <button onClick={() => setDrawerOpen(true)} className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-[11px] text-slate-400">
          <Menu size={20} />
          <span>More</span>
        </button>
      </nav>
    </div>
  )
}

function InstallBanner({ isIOS, canInstall, onInstall, onDismiss }) {
  return (
    <div className="flex items-center justify-between gap-3 bg-gold-50 border-b border-gold-100 px-4 sm:px-6 py-2.5 text-sm">
      <div className="flex items-center gap-2 min-w-0">
        <Download size={16} className="text-gold-700 shrink-0" />
        {isIOS ? (
          <span className="text-slate-700 truncate">
            Install this app: tap <Share size={13} className="inline -mt-0.5" /> Share, then <strong>"Add to Home Screen"</strong>.
          </span>
        ) : (
          <span className="text-slate-700 truncate">Install CRS Accounting on this device for quick, app-like access.</span>
        )}
      </div>
      <div className="flex items-center gap-3 shrink-0">
        {canInstall && !isIOS && (
          <button onClick={onInstall} className="text-xs font-semibold bg-navy-600 hover:bg-navy-700 text-white px-3 py-1.5 rounded-lg">
            Install
          </button>
        )}
        <button onClick={onDismiss} className="text-slate-400 hover:text-slate-600"><X size={16} /></button>
      </div>
    </div>
  )
}

function NavItem({ to, label, icon: Icon, end, alwaysShowLabel }) {
  return (
    <NavLink
      to={to} end={end}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 lg:px-5 py-3 md:py-2.5 mx-2 rounded-lg text-sm font-medium transition-colors ${
          isActive ? 'bg-navy-600 text-white' : 'text-slate-600 hover:bg-navy-50 hover:text-navy-700'
        }`
      }
      title={label}
    >
      <Icon size={19} className="shrink-0" />
      <span className={alwaysShowLabel ? 'inline truncate' : 'hidden lg:inline truncate'}>{label}</span>
    </NavLink>
  )
}

function ActiveCompanyBar({ companies, activeCompany, switchCompany, activeRole, activeProduct, availableProducts, switchProduct }) {
  const [open, setOpen] = useState(false)
  if (!activeCompany) return null

  return (
    <div className="hidden md:flex items-center justify-between px-6 lg:px-8 h-11 bg-navy-700 text-white text-sm sticky top-0 z-20">
      <div className="relative">
        <button
          onClick={() => companies.length > 1 && setOpen(o => !o)}
          className="flex items-center gap-2 font-medium"
        >
          <Building2 size={15} className="text-gold-300 shrink-0" />
          <span>Viewing: <span className="font-semibold">{activeCompany.name}</span></span>
          {companies.length > 1 && <ChevronDown size={14} className="text-navy-200" />}
        </button>
        {open && (
          <div className="absolute z-30 top-full left-0 mt-1 w-64 bg-white border border-slate-200 rounded-lg shadow-lg text-slate-700">
            {companies.map(({ company }) => (
              <button
                key={company.id}
                onClick={() => { switchCompany(company.id); setOpen(false) }}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-navy-50 truncate ${company.id === activeCompany.id ? 'font-semibold text-navy-700' : ''}`}
              >
                {company.name}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="flex items-center gap-3">
        <ProductSwitcher activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />
        {activeRole && (
          <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-white/10 capitalize">{activeRole}</span>
        )}
      </div>
    </div>
  )
}

function ProductSwitcher({ activeProduct, availableProducts, switchProduct }) {
  const [open, setOpen] = useState(false)
  if (!activeProduct || availableProducts.length === 0) return null

  if (availableProducts.length === 1) {
    return (
      <span className="flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full bg-white/10">
        <Layers size={12} className="text-gold-300" /> {PRODUCT_LABELS[activeProduct]}
      </span>
    )
  }

  return (
    <div className="relative">
      <button onClick={() => setOpen(o => !o)} className="flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full bg-white/10 hover:bg-white/20">
        <Layers size={12} className="text-gold-300" /> {PRODUCT_LABELS[activeProduct]}
        <ChevronDown size={12} className="text-navy-200" />
      </button>
      {open && (
        <div className="absolute z-30 top-full right-0 mt-1 w-56 bg-white border border-slate-200 rounded-lg shadow-lg text-slate-700">
          {availableProducts.map(product => (
            <button
              key={product}
              onClick={() => { switchProduct(product); setOpen(false) }}
              className={`w-full text-left px-3 py-2 text-sm hover:bg-navy-50 ${product === activeProduct ? 'font-semibold text-navy-700' : ''}`}
            >
              {PRODUCT_LABELS[product]}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function CompanySwitcherBlock({ companies, activeCompany, switchCompany, alwaysShowLabel }) {
  const [open, setOpen] = useState(false)
  if (!activeCompany) return null
  return (
    <div className="px-3 lg:px-4 py-3 border-b border-slate-100 relative">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between gap-2 px-2 lg:px-3 py-2 rounded-lg border border-slate-200 hover:border-navy-300 text-left"
      >
        <span className={`${alwaysShowLabel ? 'block' : 'hidden lg:block'} text-sm font-medium text-slate-700 truncate`}>{activeCompany.name}</span>
        <Building2 size={18} className={`${alwaysShowLabel ? 'hidden' : 'lg:hidden mx-auto'} text-navy-600`} />
        <ChevronDown size={14} className={`${alwaysShowLabel ? 'block' : 'hidden lg:block'} text-slate-400 shrink-0`} />
      </button>
      {open && companies.length > 1 && (
        <div className="absolute z-30 top-full left-2 right-2 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg">
          {companies.map(({ company }) => (
            <button
              key={company.id}
              onClick={() => { switchCompany(company.id); setOpen(false) }}
              className="w-full text-left px-3 py-2 text-sm hover:bg-navy-50 truncate"
            >
              {company.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
