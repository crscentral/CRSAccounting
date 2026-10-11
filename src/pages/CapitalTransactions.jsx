import { getLocalDate } from '../lib/dateUtils'
import { useEffect, useState } from 'react'
import { Plus, Trash2, Landmark, Users } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import Modal, { Field } from '../components/Modal'
import { CURRENCY_LIST } from '../lib/currencies'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import { resolveReportPeriod } from '../lib/fiscalYear'

export default function CapitalTransactions() {
  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [tab, setTab] = useState('equity')
  const [accounts, setAccounts] = useState([])
  const [loanPayments, setLoanPayments] = useState([])
  const [dividends, setDividends] = useState([])
  const [ownerContributions, setOwnerContributions] = useState([])
  const [loansTaken, setLoansTaken] = useState([])
  const [owners, setOwners] = useState([])
  const [staffList, setStaffList] = useState([])
  const [staffLoansGiven, setStaffLoansGiven] = useState([])
  const [staffLoanRepayments, setStaffLoanRepayments] = useState([])
  
  const [loanModalOpen, setLoanModalOpen] = useState(false)
  const [dividendModalOpen, setDividendModalOpen] = useState(false)
  const [contributionModalOpen, setContributionModalOpen] = useState(false)
  const [loanTakenModalOpen, setLoanTakenModalOpen] = useState(false)
  const [staffLoanGivenModalOpen, setStaffLoanGivenModalOpen] = useState(false)
  const [staffLoanRepaymentModalOpen, setStaffLoanRepaymentModalOpen] = useState(false)
  const [ownerManagerOpen, setOwnerManagerOpen] = useState(false)
  const [staffManagerOpen, setStaffManagerOpen] = useState(false)
  
  const [editItem, setEditItem] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadAll() {
    const [{ data: acc }, { data: loans }, { data: divs }, { data: contribs }, { data: taken }, { data: dbOwners }, { data: sGiven }, { data: sRepay }, { data: dbStaff }] = await Promise.all([
      supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('code'),
      supabase.from('loan_principal_payments').select('*, loan_account:accounts!loan_principal_payments_loan_account_id_fkey(name, code)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('owner_contributions').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('loans_taken').select('*, loan_account:accounts!loans_taken_loan_account_id_fkey(name, code)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('company_owners').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name'),
      supabase.from('staff_loans_given').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('staff_loan_repayments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('company_staff').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name'),
    ])
    setAccounts(acc || [])
    setLoanPayments(loans || [])
    setDividends(divs || [])
    setOwnerContributions(contribs || [])
    setLoansTaken(taken || [])
    setStaffLoansGiven(sGiven || [])
    setStaffLoanRepayments(sRepay || [])

    // Collect all owners from DB + any historical names in transactions
    const ownerMap = new Map()
    ;(dbOwners || []).forEach(o => { if (o.name?.trim()) ownerMap.set(o.name.trim(), o) })
    ;[...(contribs || []), ...(divs || []), ...(loans || []), ...(taken || [])].forEach(r => {
      if (r.owner_name?.trim() && !ownerMap.has(r.owner_name.trim())) {
        ownerMap.set(r.owner_name.trim(), { name: r.owner_name.trim() })
      }
    })
    setOwners(Array.from(ownerMap.values()).sort((a, b) => a.name.localeCompare(b.name)))

    // Collect all staff from DB + any historical names in transactions
    const staffMap = new Map()
    ;(dbStaff || []).forEach(s => { if (s.name?.trim()) staffMap.set(s.name.trim(), s) })
    ;[...(sGiven || []), ...(sRepay || [])].forEach(r => {
      if (r.staff_name?.trim() && !staffMap.has(r.staff_name.trim())) {
        staffMap.set(r.staff_name.trim(), { name: r.staff_name.trim() })
      }
    })
    setStaffList(Array.from(staffMap.values()).sort((a, b) => a.name.localeCompare(b.name)))
  }

  async function handleDelete(table, id) {
    if (!confirm('Delete this entry? This cannot be undone.')) return
    const { error } = await supabase.from(table).delete().eq('id', id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadAll()
  }


  async function generateCapitalReport(selections, format) {
    const range = resolveReportPeriod(selections.period, 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const sections = []
    if (selections.sections.includes("Owner's Equity (Contributions)")) {
      const { data } = await supabase.from('owner_contributions').select('*')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: "Owner's Equity (Contributions)",
        columns: ['Date', 'Owner', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.owner_name, `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }
    if (selections.sections.includes('Owner Loan Balance Summary')) {
      const [{ data: takenAll }, { data: repaidAll }, { data: dbOwners }] = await Promise.all([
        supabase.from('loans_taken').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('loan_principal_payments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('company_owners').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name')
      ])

      const summaryMap = {}
      ;(dbOwners || []).forEach(o => { summaryMap[o.name] = { name: o.name, taken: 0, repaid: 0 } })
      ;(takenAll || []).forEach(r => {
        const n = r.owner_name?.trim() || 'Unknown Owner'
        summaryMap[n] = summaryMap[n] || { name: n, taken: 0, repaid: 0 }
        summaryMap[n].taken += Number(r.amount_usd || 0)
      })
      ;(repaidAll || []).forEach(r => {
        const n = r.owner_name?.trim() || 'Unknown Owner'
        summaryMap[n] = summaryMap[n] || { name: n, taken: 0, repaid: 0 }
        summaryMap[n].repaid += Number(r.amount_usd || 0)
      })

      const rows = Object.values(summaryMap).map(s => {
        const bal = s.taken - s.repaid
        const status = bal > 0 ? 'To Be Paid' : bal < 0 ? 'Overpaid' : (s.taken > 0 || s.repaid > 0 ? 'Settled' : 'No Loans')
        return [
          s.name,
          f(s.taken),
          f(s.repaid),
          status,
          f(Math.abs(bal))
        ]
      })

      sections.push({
        heading: 'Owner Loan Balance Summary',
        columns: ['Owner', `Total Loans Taken (${selections.currency})`, `Total Repaid (${selections.currency})`, 'Status', `Net Balance (${selections.currency})`],
        rows,
      })
    }
    if (selections.sections.includes('Loans Taken')) {
      const { data } = await supabase.from('loans_taken').select('*, loan_account:accounts!loans_taken_loan_account_id_fkey(name, code)')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: 'Loans Taken',
        columns: ['Date', 'Owner', 'Loan Account', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.owner_name || '—', r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—', `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }
    if (selections.sections.includes('Loan Principal Repayments')) {
      const { data } = await supabase.from('loan_principal_payments').select('*, loan_account:accounts!loan_principal_payments_loan_account_id_fkey(name, code)')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: 'Loan Principal Repayments',
        columns: ['Date', 'Owner', 'Loan Account', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.owner_name || '—', r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—', `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }
    if (selections.sections.includes('Owner Dividends')) {
      const { data } = await supabase.from('owner_dividends').select('*')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: 'Owner Dividends',
        columns: ['Date', 'Owner', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.owner_name, `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }
    if (selections.sections.includes('Staff Loan Balance Summary')) {
      const [{ data: sGivenAll }, { data: sRepayAll }, { data: dbStaff }] = await Promise.all([
        supabase.from('staff_loans_given').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('staff_loan_repayments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('company_staff').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name')
      ])

      const summaryMap = {}
      ;(dbStaff || []).forEach(s => { summaryMap[s.name] = { name: s.name, taken: 0, repaid: 0 } })
      ;(sGivenAll || []).forEach(r => {
        const n = r.staff_name?.trim() || 'Unknown Staff'
        summaryMap[n] = summaryMap[n] || { name: n, taken: 0, repaid: 0 }
        summaryMap[n].taken += Number(r.amount_usd || 0)
      })
      ;(sRepayAll || []).forEach(r => {
        const n = r.staff_name?.trim() || 'Unknown Staff'
        summaryMap[n] = summaryMap[n] || { name: n, taken: 0, repaid: 0 }
        summaryMap[n].repaid += Number(r.amount_usd || 0)
      })

      const rows = Object.values(summaryMap).map(s => {
        const bal = s.taken - s.repaid
        const status = bal > 0 ? 'To Be Repaid' : bal < 0 ? 'Overpaid' : (s.taken > 0 || s.repaid > 0 ? 'Settled' : 'No Loans')
        return [
          s.name,
          f(s.taken),
          f(s.repaid),
          status,
          f(Math.abs(bal))
        ]
      })

      sections.push({
        heading: 'Staff Loan Balance Summary',
        columns: ['Staff Member', `Total Loans Given (${selections.currency})`, `Total Repaid (${selections.currency})`, 'Status', `Net Balance (${selections.currency})`],
        rows,
      })
    }
    if (selections.sections.includes('Loan Given to Staff')) {
      const { data } = await supabase.from('staff_loans_given').select('*')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: 'Loan Given to Staff',
        columns: ['Date', 'Staff Member', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.staff_name || '—', `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }
    if (selections.sections.includes('Loan Repayment From Staff')) {
      const { data } = await supabase.from('staff_loan_repayments').select('*')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: 'Loan Repayment From Staff',
        columns: ['Date', 'Staff Member', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.staff_name || '—', `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }

    const title = 'Capital & Loans'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'capital_loans_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'capital_loans_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'capital_loans_report' })
  }

  if (!activeCompany) return null

  const liabilityAccounts = accounts.filter(a => a.type === 'Liabilities')
  const cashAccounts = accounts.filter(a => a.type === 'Assets')

  // Per-owner running balance of cumulative dividends paid
  const byOwner = {}
  dividends.forEach(d => {
    byOwner[d.owner_name] = byOwner[d.owner_name] || { name: d.owner_name, total: 0 }
    byOwner[d.owner_name].total += Number(d.amount_usd)
  })
  const ownerBalances = Object.values(byOwner).sort((a, b) => b.total - a.total)

  // Per-owner loan summary: Loans Taken (money owner lent to hotel) vs Loan Repayments (money hotel repaid to owner)
  const ownerLoanMap = {}
  owners.forEach(o => {
    if (o.name) ownerLoanMap[o.name] = { name: o.name, taken: 0, repaid: 0 }
  })
  loansTaken.forEach(lt => {
    const name = lt.owner_name?.trim() || 'Unknown Owner'
    ownerLoanMap[name] = ownerLoanMap[name] || { name, taken: 0, repaid: 0 }
    ownerLoanMap[name].taken += Number(lt.amount_usd || 0)
  })
  loanPayments.forEach(lp => {
    const name = lp.owner_name?.trim() || 'Unknown Owner'
    ownerLoanMap[name] = ownerLoanMap[name] || { name, taken: 0, repaid: 0 }
    ownerLoanMap[name].repaid += Number(lp.amount_usd || 0)
  })

  const ownerLoanSummaries = Object.values(ownerLoanMap).map(s => {
    const bal = s.taken - s.repaid
    return {
      ...s,
      balance: bal,
    }
  }).sort((a, b) => {
    const aActive = a.taken > 0 || a.repaid > 0
    const bActive = b.taken > 0 || b.repaid > 0
    if (aActive && !bActive) return -1
    if (!aActive && bActive) return 1
    return a.name.localeCompare(b.name)
  })

  // Per-staff loan summary: Loans Given (money hotel lent to staff) vs Loan Repayments (money staff repaid to hotel)
  const staffLoanMap = {}
  staffList.forEach(s => {
    if (s.name) staffLoanMap[s.name] = { name: s.name, taken: 0, repaid: 0 }
  })
  staffLoansGiven.forEach(sg => {
    const name = sg.staff_name?.trim() || 'Unknown Staff'
    staffLoanMap[name] = staffLoanMap[name] || { name, taken: 0, repaid: 0 }
    staffLoanMap[name].taken += Number(sg.amount_usd || 0)
  })
  staffLoanRepayments.forEach(sr => {
    const name = sr.staff_name?.trim() || 'Unknown Staff'
    staffLoanMap[name] = staffLoanMap[name] || { name, taken: 0, repaid: 0 }
    staffLoanMap[name].repaid += Number(sr.amount_usd || 0)
  })

  const staffLoanSummaries = Object.values(staffLoanMap).map(s => {
    const bal = s.taken - s.repaid
    return {
      ...s,
      balance: bal,
    }
  }).sort((a, b) => {
    const aActive = a.taken > 0 || a.repaid > 0
    const bActive = b.taken > 0 || b.repaid > 0
    if (aActive && !bActive) return -1
    if (!aActive && bActive) return 1
    return a.name.localeCompare(b.name)
  })

  const currentList = tab === 'equity' ? ownerContributions :
                      tab === 'loans_taken' ? loansTaken :
                      tab === 'dividends' ? dividends :
                      tab === 'staff_loans_given' ? staffLoansGiven :
                      tab === 'staff_loan_repayments' ? staffLoanRepayments :
                      loanPayments

  const byCurrency = {}
  let totalUsd = 0
  currentList.forEach(i => {
    byCurrency[i.currency] = byCurrency[i.currency] || { native: 0, usd: 0, count: 0 }
    byCurrency[i.currency].native += Number(i.amount)
    byCurrency[i.currency].usd += Number(i.amount_usd)
    byCurrency[i.currency].count++
    totalUsd += Number(i.amount_usd)
  })

  return (
    <div>
      <PageHeader
        title="Capital & Loans"
        subtitle={`${activeCompany.name} • Loan principal repayments and owner dividends — balance sheet only, never part of P&L`}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-4 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin']) && (
              <button
                onClick={() => setOwnerManagerOpen(true)}
                className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-4 py-2 rounded-lg hover:border-navy-400"
              >
                <Users size={16} /> Manage Owners
              </button>
            )}
            {can(['owner', 'admin']) && (
              <button
                onClick={() => setStaffManagerOpen(true)}
                className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-4 py-2 rounded-lg hover:border-navy-400"
              >
                <Users size={16} /> Manage Staff
              </button>
            )}
            {can(['owner', 'admin']) && (
              <button
                onClick={() => {
                  setEditItem(null);
                  if (tab === 'equity') setContributionModalOpen(true);
                  else if (tab === 'loans_taken') setLoanTakenModalOpen(true);
                  else if (tab === 'dividends') setDividendModalOpen(true);
                  else if (tab === 'staff_loans_given') setStaffLoanGivenModalOpen(true);
                  else if (tab === 'staff_loan_repayments') setStaffLoanRepaymentModalOpen(true);
                  else setLoanModalOpen(true);
                }}
                className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
              >
                <Plus size={16} /> New Entry
              </button>
            )}
          </div>
        }
      />

      <div className="flex flex-wrap gap-2 mb-5">
        <button onClick={() => setTab('equity')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'equity' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Users size={15} /> Owner's Equity
        </button>
        <button onClick={() => setTab('loans_taken')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'loans_taken' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Landmark size={15} /> Loans Taken
        </button>
        <button onClick={() => setTab('loans')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'loans' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Landmark size={15} /> Loan Principal Repayments
        </button>
        <button onClick={() => setTab('dividends')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'dividends' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Users size={15} /> Owner Dividends
        </button>
        <button onClick={() => setTab('staff_loans_given')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'staff_loans_given' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Landmark size={15} /> Loan Given to Staff
        </button>
        <button onClick={() => setTab('staff_loan_repayments')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'staff_loan_repayments' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Landmark size={15} /> Loan Repayment From Staff
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-4">Currency Summary ({cp.displayCurrency} Consolidated)</h3>
        {Object.keys(byCurrency).length === 0 ? (
          <p className="text-sm text-slate-400">No transactions to summarize.</p>
        ) : (
          <div className="space-y-3">
            {Object.entries(byCurrency).map(([code, v]) => (
              <div key={code} className="flex items-center justify-between text-sm flex-wrap gap-1">
                <div>
                  <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium mr-2">{code}</span>
                  <span className="text-slate-500">{v.native.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} • {v.count} entry(s)</span>
                </div>
                <span className="font-semibold text-slate-700">{cp.fmt(v.usd)}</span>
              </div>
            ))}
            <div className="flex items-center justify-between pt-3 border-t border-slate-100 font-bold text-emerald-700">
              <span>Grand Total ({cp.displayCurrency})</span>
              <span>{cp.fmt(totalUsd)}</span>
            </div>
          </div>
        )}
      </div>


      {tab === 'equity' && (
        <>
          <p className="text-sm text-slate-500 mb-4 px-1">Record capital contributions made by owners into the business.</p>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'owner_name', label: 'Owner' },
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setContributionModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('owner_contributions', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={ownerContributions}
            emptyMessage="No owner contributions recorded."
          />
        </>
      )}

      {tab === 'loans_taken' && (
        <>
          <OwnerLoanCards summaries={ownerLoanSummaries} fmt={cp.fmt} />
          <p className="text-sm text-slate-500 mb-4 px-1">Record new loans received by the business.</p>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'owner_name', label: 'Owner', render: r => r.owner_name || '—' },
              { key: 'loan_account', label: 'Loan Account', render: r => r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—' },
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setLoanTakenModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('loans_taken', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={loansTaken}
            emptyMessage="No loans taken recorded."
          />
        </>
      )}

      {tab === 'loans' && (
        <>
          <OwnerLoanCards summaries={ownerLoanSummaries} fmt={cp.fmt} />
          <p className="text-sm text-slate-500 mb-4 px-1">Record loan principal repayments made by the business. This tracks only the principal portion — record Loan Interest as a normal expense via Purchase Invoices instead, since interest (not principal) belongs in the P&L.</p>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'owner_name', label: 'Owner', render: r => r.owner_name || '—' },
              { key: 'loan_account', label: 'Loan Account', render: r => r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—' },
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setLoanModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('loan_principal_payments', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={loanPayments}
            emptyMessage="No loan principal repayments recorded."
          />
        </>
      )}

      {tab === 'dividends' && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {ownerBalances.map(o => (
              <div key={o.name} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                <div className="text-sm font-semibold text-slate-600">{o.name}</div>
                <div className="text-xl font-bold text-slate-800 mt-1">{cp.fmt(o.total)}</div>
                <div className="text-xs text-slate-400 mt-1">Total dividends paid</div>
              </div>
            ))}
          </div>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'owner_name', label: 'Owner' },
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setDividendModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('owner_dividends', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={dividends}
            emptyMessage="No owner dividend entries yet."
          />
        </>
      )}

      {tab === 'staff_loans_given' && (
        <>
          <StaffLoanCards summaries={staffLoanSummaries} fmt={cp.fmt} />
          <p className="text-sm text-slate-500 mb-4 px-1">Record loans and advances given to hotel staff.</p>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'staff_name', label: 'Staff Member', render: r => r.staff_name || '—' },
              { key: 'cash_account', label: 'Paid From (Cash/Bank)', render: r => {
                const acc = accounts.find(a => a.id === r.cash_account_id)
                return acc ? `${acc.code} - ${acc.name}` : '—'
              }},
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setStaffLoanGivenModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('staff_loans_given', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={staffLoansGiven}
            emptyMessage="No loans given to staff recorded."
          />
        </>
      )}

      {tab === 'staff_loan_repayments' && (
        <>
          <StaffLoanCards summaries={staffLoanSummaries} fmt={cp.fmt} />
          <p className="text-sm text-slate-500 mb-4 px-1">Record loan repayments received from hotel staff.</p>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'staff_name', label: 'Staff Member', render: r => r.staff_name || '—' },
              { key: 'cash_account', label: 'Received Into (Cash/Bank)', render: r => {
                const acc = accounts.find(a => a.id === r.cash_account_id)
                return acc ? `${acc.code} - ${acc.name}` : '—'
              }},
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setStaffLoanRepaymentModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('staff_loan_repayments', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={staffLoanRepayments}
            emptyMessage="No loan repayments from staff recorded."
          />
        </>
      )}



      {ownerManagerOpen && (
        <ManageOwnersModal
          companyId={activeCompany.id}
          product={activeProduct}
          owners={owners}
          onClose={() => setOwnerManagerOpen(false)}
          onRefresh={loadAll}
        />
      )}
      {staffManagerOpen && (
        <ManageStaffModal
          companyId={activeCompany.id}
          product={activeProduct}
          staffList={staffList}
          onClose={() => setStaffManagerOpen(false)}
          onRefresh={loadAll}
        />
      )}
      {staffLoanGivenModalOpen && (
        <StaffLoanGivenFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          initialData={editItem}
          cashAccounts={cashAccounts}
          staffList={staffList}
          onStaffAdded={(name) => { setStaffList(prev => prev.some(s => s.name === name) ? prev : [...prev, { name }].sort((a,b)=>a.name.localeCompare(b.name))) }}
          onClose={() => { setStaffLoanGivenModalOpen(false); setEditItem(null); }}
          onSaved={loadAll}
        />
      )}
      {staffLoanRepaymentModalOpen && (
        <StaffLoanRepaymentFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          initialData={editItem}
          cashAccounts={cashAccounts}
          staffList={staffList}
          onStaffAdded={(name) => { setStaffList(prev => prev.some(s => s.name === name) ? prev : [...prev, { name }].sort((a,b)=>a.name.localeCompare(b.name))) }}
          onClose={() => { setStaffLoanRepaymentModalOpen(false); setEditItem(null); }}
          onSaved={loadAll}
        />
      )}
      {contributionModalOpen && (
        <OwnerEquityFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          initialData={editItem}
          cashAccounts={cashAccounts}
          owners={owners}
          onOwnerAdded={(name) => { setOwners(prev => prev.some(o => o.name === name) ? prev : [...prev, { name }].sort((a,b)=>a.name.localeCompare(b.name))) }}
          onClose={() => { setContributionModalOpen(false); setEditItem(null); }}
          onSaved={loadAll}
        />
      )}
      {loanTakenModalOpen && (
        <LoanTakenFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          initialData={editItem}
          liabilityAccounts={liabilityAccounts}
          cashAccounts={cashAccounts}
          owners={owners}
          onOwnerAdded={(name) => { setOwners(prev => prev.some(o => o.name === name) ? prev : [...prev, { name }].sort((a,b)=>a.name.localeCompare(b.name))) }}
          onClose={() => { setLoanTakenModalOpen(false); setEditItem(null); }}
          onSaved={loadAll}
        />
      )}
      {loanModalOpen && (
        <LoanRepaymentFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          initialData={editItem}
          liabilityAccounts={liabilityAccounts}
          cashAccounts={cashAccounts}
          owners={owners}
          onOwnerAdded={(name) => { setOwners(prev => prev.some(o => o.name === name) ? prev : [...prev, { name }].sort((a,b)=>a.name.localeCompare(b.name))) }}
          onClose={() => { setLoanModalOpen(false); setEditItem(null); }}
          onSaved={loadAll}
        />
      )}
      {dividendModalOpen && (
        <DividendFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          initialData={editItem}
          cashAccounts={cashAccounts}
          owners={owners}
          onOwnerAdded={(name) => { setOwners(prev => prev.some(o => o.name === name) ? prev : [...prev, { name }].sort((a,b)=>a.name.localeCompare(b.name))) }}
          onClose={() => { setDividendModalOpen(false); setEditItem(null); }}
          onSaved={loadAll}
        />
      )}
      {reportModalOpen && (
        <ReportOptionsModal
          title="Capital & Loans"
          fields={[
            { type: 'checkboxGroup', key: 'sections', label: 'Include Sections', options: ["Owner's Equity (Contributions)", 'Owner Loan Balance Summary', 'Loans Taken', 'Loan Principal Repayments', 'Owner Dividends', 'Staff Loan Balance Summary', 'Loan Given to Staff', 'Loan Repayment From Staff'], default: ["Owner's Equity (Contributions)", 'Owner Loan Balance Summary', 'Loans Taken', 'Loan Principal Repayments', 'Owner Dividends', 'Staff Loan Balance Summary', 'Loan Given to Staff', 'Loan Repayment From Staff'] },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateCapitalReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function OwnerLoanCards({ summaries = [], fmt }) {
  if (!summaries || summaries.length === 0) return null

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-3 px-1">
        <h4 className="font-semibold text-slate-800 text-sm">Owner Loan Balances</h4>
        <span className="text-xs text-slate-400">Net balance per owner (Loans Taken − Repayments)</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {summaries.map(s => {
          const isToBePaid = s.balance > 0
          const isOverpaid = s.balance < 0
          const isSettled = s.balance === 0 && (s.taken > 0 || s.repaid > 0)
          const isNoActivity = s.taken === 0 && s.repaid === 0

          return (
            <div
              key={s.name}
              className={`bg-white border rounded-xl p-4 shadow-sm transition-all ${
                isToBePaid
                  ? 'border-emerald-200 bg-emerald-50/20'
                  : isOverpaid
                  ? 'border-rose-200 bg-rose-50/20'
                  : 'border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-slate-800 text-sm truncate" title={s.name}>
                  {s.name}
                </span>
                <span className="text-[10px] font-medium uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                  Owner
                </span>
              </div>

              <div className="mt-2.5">
                {isToBePaid && (
                  <div>
                    <div className="text-xl font-bold text-emerald-600">
                      {fmt(s.balance)}
                    </div>
                    <div className="text-xs font-semibold text-emerald-700 mt-0.5 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
                      To Be Paid
                    </div>
                  </div>
                )}
                {isOverpaid && (
                  <div>
                    <div className="text-xl font-bold text-rose-600">
                      {fmt(Math.abs(s.balance))}
                    </div>
                    <div className="text-xs font-semibold text-rose-700 mt-0.5 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-500 inline-block"></span>
                      Overpaid
                    </div>
                  </div>
                )}
                {isSettled && (
                  <div>
                    <div className="text-xl font-bold text-slate-700">
                      {fmt(0)}
                    </div>
                    <div className="text-xs font-medium text-slate-500 mt-0.5">
                      Fully Settled
                    </div>
                  </div>
                )}
                {isNoActivity && (
                  <div>
                    <div className="text-xl font-bold text-slate-400">
                      {fmt(0)}
                    </div>
                    <div className="text-xs font-medium text-slate-400 mt-0.5">
                      No Loans Recorded
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-3 pt-2.5 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs text-slate-500">
                <div>
                  <div className="text-[11px] text-slate-400">Loan Taken</div>
                  <div className="font-medium text-slate-700">{fmt(s.taken)}</div>
                </div>
                <div>
                  <div className="text-[11px] text-slate-400">Repaid</div>
                  <div className="font-medium text-slate-700">{fmt(s.repaid)}</div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function OwnerSelectField({ value, onChange, owners = [], companyId, product, onOwnerAdded }) {
  const [isAdding, setIsAdding] = useState(false)
  const [newOwnerName, setNewOwnerName] = useState('')
  const [savingOwner, setSavingOwner] = useState(false)

  async function handleAddOwner(e) {
    if (e) e.preventDefault()
    const trimmed = newOwnerName.trim()
    if (!trimmed) return
    setSavingOwner(true)
    try {
      const { error } = await supabase.from('company_owners').insert({
        company_id: companyId,
        product,
        name: trimmed,
      })
      if (error && !error.message.includes('unique')) throw error
      if (onOwnerAdded) onOwnerAdded(trimmed)
      onChange(trimmed)
      setNewOwnerName('')
      setIsAdding(false)
    } catch (err) {
      alert('Error adding owner: ' + err.message)
    } finally {
      setSavingOwner(false)
    }
  }

  const allOwners = [...owners]
  if (value && !allOwners.some(o => o.name === value)) {
    allOwners.unshift({ name: value })
  }

  return (
    <Field label="Owner Name *">
      {isAdding ? (
        <div className="flex gap-2">
          <input
            type="text"
            required
            autoFocus
            placeholder="Enter owner name…"
            value={newOwnerName}
            onChange={e => setNewOwnerName(e.target.value)}
            className="flex-1 h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
          />
          <button
            type="button"
            disabled={savingOwner}
            onClick={handleAddOwner}
            className="px-3 h-10 bg-navy-600 hover:bg-navy-700 text-white rounded-lg text-xs font-semibold whitespace-nowrap"
          >
            {savingOwner ? 'Adding…' : 'Save'}
          </button>
          <button
            type="button"
            onClick={() => setIsAdding(false)}
            className="px-3 h-10 border border-slate-300 hover:bg-slate-50 text-slate-600 rounded-lg text-xs font-semibold whitespace-nowrap bg-white"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div className="flex gap-2">
          <select
            required
            value={value}
            onChange={e => {
              if (e.target.value === '__add_new__') {
                setIsAdding(true)
              } else {
                onChange(e.target.value)
              }
            }}
            className="flex-1 h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
          >
            <option value="">Select owner…</option>
            {allOwners.map(o => (
              <option key={o.id || o.name} value={o.name}>{o.name}</option>
            ))}
            <option value="__add_new__">+ Add New Owner…</option>
          </select>
          <button
            type="button"
            onClick={() => setIsAdding(true)}
            className="px-3 h-10 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1 whitespace-nowrap bg-white"
          >
            <Plus size={14} /> New Owner
          </button>
        </div>
      )}
    </Field>
  )
}

function ManageOwnersModal({ companyId, product, owners = [], onClose, onRefresh }) {
  const [newOwner, setNewOwner] = useState('')
  const [saving, setSaving] = useState(false)
  const [deletingId, setDeletingId] = useState(null)

  async function handleAdd(e) {
    e.preventDefault()
    if (!newOwner.trim()) return
    setSaving(true)
    try {
      const { error } = await supabase.from('company_owners').insert({
        company_id: companyId,
        product,
        name: newOwner.trim()
      })
      if (error && !error.message.includes('unique')) throw error
      setNewOwner('')
      onRefresh()
    } catch (err) {
      alert('Error adding owner: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleDeleteOwner(owner) {
    if (!confirm(`Delete owner "${owner.name}"?`)) return
    if (!owner.id) {
      alert('This owner was inferred from transactions and cannot be deleted until transaction records are updated.')
      return
    }
    setDeletingId(owner.id)
    try {
      const { error } = await supabase.from('company_owners').delete().eq('id', owner.id)
      if (error) throw error
      onRefresh()
    } catch (err) {
      alert('Error deleting owner: ' + err.message)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <Modal title="Manage Owners" onClose={onClose}>
      <div className="space-y-4">
        <p className="text-xs text-slate-500">
          Add and manage company owners. Owners can be linked across Owner's Equity, Loans Taken, Loan Repayments, and Dividends.
        </p>

        <form onSubmit={handleAdd} className="flex gap-2">
          <input
            type="text"
            required
            placeholder="New owner name…"
            value={newOwner}
            onChange={e => setNewOwner(e.target.value)}
            className="flex-1 h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
          />
          <button
            type="submit"
            disabled={saving}
            className="bg-navy-600 hover:bg-navy-700 text-white text-sm font-semibold px-4 h-10 rounded-lg disabled:opacity-50 flex items-center gap-1 whitespace-nowrap"
          >
            <Plus size={16} /> Add Owner
          </button>
        </form>

        <div className="border border-slate-200 rounded-lg divide-y divide-slate-100 max-h-60 overflow-y-auto">
          {owners.length === 0 ? (
            <div className="p-4 text-center text-sm text-slate-400">No owners created yet.</div>
          ) : (
            owners.map(o => (
              <div key={o.name} className="flex items-center justify-between p-3 text-sm">
                <span className="font-medium text-slate-700">{o.name}</span>
                {o.id && (
                  <button
                    onClick={() => handleDeleteOwner(o)}
                    disabled={deletingId === o.id}
                    className="text-slate-400 hover:text-red-600 p-1"
                    title="Delete owner"
                  >
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
            ))
          )}
        </div>

        <div className="pt-2">
          <button type="button" onClick={onClose} className="w-full border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 bg-white">
            Close
          </button>
        </div>
      </div>
    </Modal>
  )
}

function LoanRepaymentFormModal({ companyId, product, liabilityAccounts, cashAccounts, initialData, owners, onOwnerAdded, onClose, onSaved }) {
  const [ownerName, setOwnerName] = useState(initialData?.owner_name || '')
  const [paymentDate, setPaymentDate] = useState(initialData?.payment_date || getLocalDate())
  const [loanAccountId, setLoanAccountId] = useState(initialData?.loan_account_id || liabilityAccounts[0]?.id || '')
  const [cashAccountId, setCashAccountId] = useState(initialData?.cash_account_id || cashAccounts[0]?.id || '')
  const [currency, setCurrency] = useState(initialData?.currency || 'USD')
  const [amount, setAmount] = useState(initialData?.amount ?? '')
  const [notes, setNotes] = useState(initialData?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!loanAccountId || !cashAccountId || !amount || Number(amount) <= 0) { setError('Loan account, cash account, and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, payment_date: paymentDate,
        owner_name: ownerName?.trim() || null,
        loan_account_id: loanAccountId, cash_account_id: cashAccountId,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err;
      if (initialData) {
        ({ error: err } = await supabase.from('loan_principal_payments').update(payload).eq('id', initialData.id))
      } else {
        ({ error: err } = await supabase.from('loan_principal_payments').insert(payload))
      }
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={initialData ? "Edit Loan Principal Repayment" : "New Loan Principal Repayment"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          This records only the principal portion of an EMI/loan payment — it reduces the loan balance and your cash, but is NOT an expense. If your payment also includes interest, record that separately as a normal expense (e.g. via a Purchase Invoice against a "Loan Interest" account).
        </p>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        <OwnerSelectField
          value={ownerName}
          onChange={setOwnerName}
          owners={owners}
          companyId={companyId}
          product={product}
          onOwnerAdded={onOwnerAdded}
        />
        <Field label="Loan Account (Liability) *">
          <select required value={loanAccountId} onChange={e => setLoanAccountId(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
            <option value="">Select loan account…</option>
            {liabilityAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <Field label="Paid From (Cash/Bank Account) *">
          <select required value={cashAccountId} onChange={e => setCashAccountId(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
            <option value="">Select cash account…</option>
            {cashAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Principal Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 bg-white hover:bg-slate-50">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}

function DividendFormModal({ companyId, product, initialData, owners, onOwnerAdded, onClose, onSaved }) {
  const [ownerName, setOwnerName] = useState(initialData?.owner_name || '')
  const [paymentDate, setPaymentDate] = useState(initialData?.payment_date || getLocalDate())
  const [currency, setCurrency] = useState(initialData?.currency || 'USD')
  const [amount, setAmount] = useState(initialData?.amount ?? '')
  const [notes, setNotes] = useState(initialData?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!ownerName.trim() || !amount || Number(amount) <= 0) { setError('Owner name and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, owner_name: ownerName.trim(), payment_date: paymentDate,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err;
      if (initialData) {
        ({ error: err } = await supabase.from('owner_dividends').update(payload).eq('id', initialData.id))
      } else {
        ({ error: err } = await supabase.from('owner_dividends').insert(payload))
      }
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={initialData ? "Edit Owner Dividend" : "New Owner Dividend"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          This records a dividend/withdrawal paid to an owner. It reduces Retained Earnings (Equity) and reduces Cash (Asset). It is NOT an expense.
        </p>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        <OwnerSelectField
          value={ownerName}
          onChange={setOwnerName}
          owners={owners}
          companyId={companyId}
          product={product}
          onOwnerAdded={onOwnerAdded}
        />
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 bg-white hover:bg-slate-50">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}

function OwnerEquityFormModal({ companyId, product, cashAccounts, initialData, owners, onOwnerAdded, onClose, onSaved }) {
  const [ownerName, setOwnerName] = useState(initialData?.owner_name || '')
  const [paymentDate, setPaymentDate] = useState(initialData?.payment_date || getLocalDate())
  const [currency, setCurrency] = useState(initialData?.currency || 'USD')
  const [amount, setAmount] = useState(initialData?.amount ?? '')
  const [notes, setNotes] = useState(initialData?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!ownerName.trim() || !amount || Number(amount) <= 0) { setError('Owner name and positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, owner_name: ownerName.trim(), payment_date: paymentDate,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      
      let err;
      if (initialData) {
        ({ error: err } = await supabase.from('owner_contributions').update(payload).eq('id', initialData.id))
      } else {
        ({ error: err } = await supabase.from('owner_contributions').insert(payload))
      }
      if (err) throw err
      
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={initialData ? "Edit Owner's Equity" : "New Owner's Equity (Contribution)"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          Record capital contributions from owners. This increases Cash (Asset) and increases Owner's Contribution (Equity).
        </p>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        <OwnerSelectField
          value={ownerName}
          onChange={setOwnerName}
          owners={owners}
          companyId={companyId}
          product={product}
          onOwnerAdded={onOwnerAdded}
        />
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 bg-white hover:bg-slate-50">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}

function LoanTakenFormModal({ companyId, product, liabilityAccounts, cashAccounts, initialData, owners, onOwnerAdded, onClose, onSaved }) {
  const [ownerName, setOwnerName] = useState(initialData?.owner_name || '')
  const [paymentDate, setPaymentDate] = useState(initialData?.payment_date || getLocalDate())
  const [loanAccountId, setLoanAccountId] = useState(initialData?.loan_account_id || liabilityAccounts[0]?.id || '')
  const [cashAccountId, setCashAccountId] = useState(initialData?.cash_account_id || cashAccounts[0]?.id || '')
  const [currency, setCurrency] = useState(initialData?.currency || 'USD')
  const [amount, setAmount] = useState(initialData?.amount ?? '')
  const [notes, setNotes] = useState(initialData?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!loanAccountId || !cashAccountId || !amount || Number(amount) <= 0) { setError('Loan account, cash account, and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, payment_date: paymentDate,
        owner_name: ownerName?.trim() || null,
        loan_account_id: loanAccountId, cash_account_id: cashAccountId,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      
      let err;
      if (initialData) {
        ({ error: err } = await supabase.from('loans_taken').update(payload).eq('id', initialData.id))
      } else {
        ({ error: err } = await supabase.from('loans_taken').insert(payload))
      }
      if (err) throw err
      
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={initialData ? "Edit Loan Taken" : "New Loan Taken"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          Record bank loans received. This increases Cash (Asset) and increases Loan Balance (Liability).
        </p>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        <OwnerSelectField
          value={ownerName}
          onChange={setOwnerName}
          owners={owners}
          companyId={companyId}
          product={product}
          onOwnerAdded={onOwnerAdded}
        />
        <Field label="Loan Account (Liability) *">
          <select required value={loanAccountId} onChange={e => setLoanAccountId(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
            <option value="">Select loan account…</option>
            {liabilityAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <Field label="Received Into (Cash/Bank Account) *">
          <select required value={cashAccountId} onChange={e => setCashAccountId(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
            <option value="">Select cash account…</option>
            {cashAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 bg-white hover:bg-slate-50">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}


function StaffLoanCards({ summaries = [], fmt }) {
  if (!summaries || summaries.length === 0) return null

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-3 px-1">
        <h4 className="font-semibold text-slate-800 text-sm">Staff Loan Balances</h4>
        <span className="text-xs text-slate-400">Net balance per staff member (Loans Given − Repayments)</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {summaries.map(s => {
          const isToBePaid = s.balance > 0
          const isOverpaid = s.balance < 0
          const isSettled = s.balance === 0 && (s.taken > 0 || s.repaid > 0)
          const isNoActivity = s.taken === 0 && s.repaid === 0

          return (
            <div
              key={s.name}
              className={`bg-white border rounded-xl p-4 shadow-sm transition-all ${
                isToBePaid
                  ? 'border-emerald-200 bg-emerald-50/20'
                  : isOverpaid
                  ? 'border-rose-200 bg-rose-50/20'
                  : 'border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-slate-800 text-sm truncate" title={s.name}>
                  {s.name}
                </span>
                <span className="text-[10px] font-medium uppercase px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">
                  Staff
                </span>
              </div>

              <div className="mt-2.5">
                {isToBePaid && (
                  <div>
                    <div className="text-xl font-bold text-emerald-600">
                      {fmt(s.balance)}
                    </div>
                    <div className="text-xs font-semibold text-emerald-700 mt-0.5 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
                      To Be Repaid
                    </div>
                  </div>
                )}
                {isOverpaid && (
                  <div>
                    <div className="text-xl font-bold text-rose-600">
                      {fmt(Math.abs(s.balance))}
                    </div>
                    <div className="text-xs font-semibold text-rose-700 mt-0.5 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-500 inline-block"></span>
                      Overpaid
                    </div>
                  </div>
                )}
                {isSettled && (
                  <div>
                    <div className="text-xl font-bold text-slate-700">
                      {fmt(0)}
                    </div>
                    <div className="text-xs font-medium text-slate-500 mt-0.5">
                      Fully Settled
                    </div>
                  </div>
                )}
                {isNoActivity && (
                  <div>
                    <div className="text-xl font-bold text-slate-400">
                      {fmt(0)}
                    </div>
                    <div className="text-xs font-medium text-slate-400 mt-0.5">
                      No Loans Recorded
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-3 pt-2.5 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs text-slate-500">
                <div>
                  <div className="text-[11px] text-slate-400">Loan Given</div>
                  <div className="font-medium text-slate-700">{fmt(s.taken)}</div>
                </div>
                <div>
                  <div className="text-[11px] text-slate-400">Repaid</div>
                  <div className="font-medium text-slate-700">{fmt(s.repaid)}</div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function StaffSelectField({ value, onChange, staffList = [], companyId, product, onStaffAdded }) {
  const [isAdding, setIsAdding] = useState(false)
  const [newStaffName, setNewStaffName] = useState('')
  const [savingStaff, setSavingStaff] = useState(false)

  async function handleAddStaff(e) {
    if (e) e.preventDefault()
    const trimmed = newStaffName.trim()
    if (!trimmed) return
    setSavingStaff(true)
    try {
      const { error } = await supabase.from('company_staff').insert({
        company_id: companyId,
        product,
        name: trimmed,
      })
      if (error && !error.message.includes('unique')) throw error
      if (onStaffAdded) onStaffAdded(trimmed)
      onChange(trimmed)
      setNewStaffName('')
      setIsAdding(false)
    } catch (err) {
      alert('Error adding staff: ' + err.message)
    } finally {
      setSavingStaff(false)
    }
  }

  const allStaff = [...staffList]
  if (value && !allStaff.some(s => s.name === value)) {
    allStaff.unshift({ name: value })
  }

  return (
    <Field label="Staff Member *">
      {isAdding ? (
        <div className="flex gap-2">
          <input
            type="text"
            required
            autoFocus
            placeholder="Enter staff name…"
            value={newStaffName}
            onChange={e => setNewStaffName(e.target.value)}
            className="flex-1 h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
          />
          <button
            type="button"
            disabled={savingStaff}
            onClick={handleAddStaff}
            className="px-3 h-10 bg-navy-600 hover:bg-navy-700 text-white rounded-lg text-xs font-semibold whitespace-nowrap"
          >
            {savingStaff ? 'Adding…' : 'Save'}
          </button>
          <button
            type="button"
            onClick={() => setIsAdding(false)}
            className="px-3 h-10 border border-slate-300 hover:bg-slate-50 text-slate-600 rounded-lg text-xs font-semibold whitespace-nowrap bg-white"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div className="flex gap-2">
          <select
            required
            value={value}
            onChange={e => {
              if (e.target.value === '__add_new__') {
                setIsAdding(true)
              } else {
                onChange(e.target.value)
              }
            }}
            className="flex-1 h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
          >
            <option value="">Select staff member…</option>
            {allStaff.map(s => (
              <option key={s.id || s.name} value={s.name}>{s.name}</option>
            ))}
            <option value="__add_new__">+ Add New Staff…</option>
          </select>
          <button
            type="button"
            onClick={() => setIsAdding(true)}
            className="px-3 h-10 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1 whitespace-nowrap bg-white"
          >
            <Plus size={14} /> New Staff
          </button>
        </div>
      )}
    </Field>
  )
}

function ManageStaffModal({ companyId, product, staffList = [], onClose, onRefresh }) {
  const [newStaff, setNewStaff] = useState('')
  const [saving, setSaving] = useState(false)
  const [deletingId, setDeletingId] = useState(null)

  async function handleAdd(e) {
    e.preventDefault()
    if (!newStaff.trim()) return
    setSaving(true)
    try {
      const { error } = await supabase.from('company_staff').insert({
        company_id: companyId,
        product,
        name: newStaff.trim()
      })
      if (error && !error.message.includes('unique')) throw error
      setNewStaff('')
      onRefresh()
    } catch (err) {
      alert('Error adding staff: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleDeleteStaff(staff) {
    if (!confirm(`Delete staff member "${staff.name}"?`)) return
    if (!staff.id) {
      alert('This staff member was inferred from transactions and cannot be deleted until transaction records are updated.')
      return
    }
    setDeletingId(staff.id)
    try {
      const { error } = await supabase.from('company_staff').delete().eq('id', staff.id)
      if (error) throw error
      onRefresh()
    } catch (err) {
      alert('Error deleting staff: ' + err.message)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <Modal title="Manage Staff" onClose={onClose}>
      <div className="space-y-4">
        <p className="text-xs text-slate-500">
          Add and manage hotel staff members for loans given and repayments.
        </p>

        <form onSubmit={handleAdd} className="flex gap-2">
          <input
            type="text"
            required
            placeholder="New staff name…"
            value={newStaff}
            onChange={e => setNewStaff(e.target.value)}
            className="flex-1 h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
          />
          <button
            type="submit"
            disabled={saving}
            className="bg-navy-600 hover:bg-navy-700 text-white text-sm font-semibold px-4 h-10 rounded-lg disabled:opacity-50 flex items-center gap-1 whitespace-nowrap"
          >
            <Plus size={16} /> Add Staff
          </button>
        </form>

        <div className="border border-slate-200 rounded-lg divide-y divide-slate-100 max-h-60 overflow-y-auto">
          {staffList.length === 0 ? (
            <div className="p-4 text-center text-sm text-slate-400">No staff members created yet.</div>
          ) : (
            staffList.map(s => (
              <div key={s.name} className="flex items-center justify-between p-3 text-sm">
                <span className="font-medium text-slate-700">{s.name}</span>
                {s.id && (
                  <button
                    onClick={() => handleDeleteStaff(s)}
                    disabled={deletingId === s.id}
                    className="text-slate-400 hover:text-red-600 p-1"
                    title="Delete staff"
                  >
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
            ))
          )}
        </div>

        <div className="pt-2">
          <button type="button" onClick={onClose} className="w-full border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 bg-white">
            Close
          </button>
        </div>
      </div>
    </Modal>
  )
}

function StaffLoanGivenFormModal({ companyId, product, initialData, cashAccounts, staffList, onStaffAdded, onClose, onSaved }) {
  const [staffName, setStaffName] = useState(initialData?.staff_name || '')
  const [paymentDate, setPaymentDate] = useState(initialData?.payment_date || getLocalDate())
  const [cashAccountId, setCashAccountId] = useState(initialData?.cash_account_id || cashAccounts[0]?.id || '')
  const [currency, setCurrency] = useState(initialData?.currency || 'USD')
  const [amount, setAmount] = useState(initialData?.amount ?? '')
  const [notes, setNotes] = useState(initialData?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!staffName.trim() || !amount || Number(amount) <= 0) {
      setError('Staff name and a positive amount are required.')
      return
    }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId,
        product,
        payment_date: paymentDate,
        staff_name: staffName.trim(),
        cash_account_id: cashAccountId || null,
        currency,
        fx_rate_locked: fxRate,
        amount: Number(amount),
        amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err
      if (initialData) {
        ({ error: err } = await supabase.from('staff_loans_given').update(payload).eq('id', initialData.id))
      } else {
        ({ error: err } = await supabase.from('staff_loans_given').insert(payload))
      }
      if (err) throw err
      onSaved()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={initialData ? "Edit Loan Given to Staff" : "New Loan Given to Staff"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          Record a loan or advance paid to a staff member. This reduces Cash (Asset) and creates a staff loan balance to be recovered.
        </p>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        <StaffSelectField
          value={staffName}
          onChange={setStaffName}
          staffList={staffList}
          companyId={companyId}
          product={product}
          onStaffAdded={onStaffAdded}
        />
        <Field label="Paid From (Cash/Bank Account)">
          <select value={cashAccountId} onChange={e => setCashAccountId(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
            <option value="">Select cash account…</option>
            {cashAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 bg-white hover:bg-slate-50">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}

function StaffLoanRepaymentFormModal({ companyId, product, initialData, cashAccounts, staffList, onStaffAdded, onClose, onSaved }) {
  const [staffName, setStaffName] = useState(initialData?.staff_name || '')
  const [paymentDate, setPaymentDate] = useState(initialData?.payment_date || getLocalDate())
  const [cashAccountId, setCashAccountId] = useState(initialData?.cash_account_id || cashAccounts[0]?.id || '')
  const [currency, setCurrency] = useState(initialData?.currency || 'USD')
  const [amount, setAmount] = useState(initialData?.amount ?? '')
  const [notes, setNotes] = useState(initialData?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!staffName.trim() || !amount || Number(amount) <= 0) {
      setError('Staff name and a positive amount are required.')
      return
    }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId,
        product,
        payment_date: paymentDate,
        staff_name: staffName.trim(),
        cash_account_id: cashAccountId || null,
        currency,
        fx_rate_locked: fxRate,
        amount: Number(amount),
        amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err
      if (initialData) {
        ({ error: err } = await supabase.from('staff_loan_repayments').update(payload).eq('id', initialData.id))
      } else {
        ({ error: err } = await supabase.from('staff_loan_repayments').insert(payload))
      }
      if (err) throw err
      onSaved()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={initialData ? "Edit Loan Repayment From Staff" : "New Loan Repayment From Staff"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          Record a loan repayment received from a staff member. This increases Cash (Asset) and reduces the staff member's outstanding loan.
        </p>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        <StaffSelectField
          value={staffName}
          onChange={setStaffName}
          staffList={staffList}
          companyId={companyId}
          product={product}
          onStaffAdded={onStaffAdded}
        />
        <Field label="Received Into (Cash/Bank Account)">
          <select value={cashAccountId} onChange={e => setCashAccountId(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
            <option value="">Select cash account…</option>
            {cashAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full h-10 border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 bg-white hover:bg-slate-50">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}
