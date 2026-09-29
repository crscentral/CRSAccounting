import { useEffect, useState } from 'react'
import { Trash2 } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function Ledger() {
  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [accounts, setAccounts] = useState([])
  const [accountId, setAccountId] = useState('')
  const [entries, setEntries] = useState([])
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAccounts() }, [activeCompany, activeProduct])
  useEffect(() => { if (accountId) loadEntries() }, [accountId, cp.range.from, cp.range.to])

  async function loadAccounts() {
    const { data } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('code')
    setAccounts(data || [])
    if (data && data.length > 0) setAccountId(data.find(a => a.code === '4010')?.id || data[0].id)
  }

  async function loadEntries() {
    const { data } = await supabase
      .from('ledger_entries')
      .select('*')
      .eq('company_id', activeCompany.id)
      .eq('account_id', accountId)
      .gte('entry_date', cp.range.from)
      .lte('entry_date', cp.range.to)
      .order('entry_date')
      
    let combined = data || []
    
    // CAPITAL & LOANS (Applies to all modes)
    const selectedAccount = (accounts || []).find(a => a.id === accountId)
    if (selectedAccount) {
      const isEqCont = ((selectedAccount.name || '').toLowerCase().includes('contribution') || (selectedAccount.name || '').toLowerCase().includes('equity')) && selectedAccount.type === 'Equity'
      const isEqDiv = ((selectedAccount.name || '').toLowerCase().includes('dividend') || (selectedAccount.name || '').toLowerCase().includes('draw') || (selectedAccount.name || '').toLowerCase().includes('retained')) && selectedAccount.type === 'Equity'
      const isCash = (selectedAccount.name || '').toLowerCase().includes('cash on hand') || (selectedAccount.name || '').toLowerCase().includes('cash')
      
      const [{ data: oCont }, { data: oDiv }, { data: lTake }, { data: lRepay }] = await Promise.all([
        supabase.from('owner_contributions').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to),
        supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to),
        supabase.from('loans_taken').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to),
        supabase.from('loan_principal_payments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to)
      ])
      
      ;(oCont || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (isEqCont) combined.push({ id: `oc-eq-${r.id}`, entry_date: r.payment_date, description: `Owner Contribution: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          if (isCash) combined.push({ id: `oc-c-${r.id}`, entry_date: r.payment_date, description: `Owner Contribution: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        }
      })
      
      ;(oDiv || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (isEqDiv) combined.push({ id: `od-eq-${r.id}`, entry_date: r.payment_date, description: `Owner Dividend: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          if (isCash) combined.push({ id: `od-c-${r.id}`, entry_date: r.payment_date, description: `Owner Dividend: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        }
      })
      
      ;(lTake || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (selectedAccount.id === r.loan_account_id) combined.push({ id: `lt-l-${r.id}`, entry_date: r.payment_date, description: `Loan Taken: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          if ((r.cash_account_id && selectedAccount.id === r.cash_account_id) || (!r.cash_account_id && isCash)) combined.push({ id: `lt-c-${r.id}`, entry_date: r.payment_date, description: `Loan Taken: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        }
      })
      
      ;(lRepay || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (selectedAccount.id === r.loan_account_id) combined.push({ id: `lr-l-${r.id}`, entry_date: r.payment_date, description: `Loan Repayment: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          if ((r.cash_account_id && selectedAccount.id === r.cash_account_id) || (!r.cash_account_id && isCash)) combined.push({ id: `lr-c-${r.id}`, entry_date: r.payment_date, description: `Loan Repayment: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        }
      })
      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const selectedAccount = (accounts || []).find(a => a.id === accountId)
      if (selectedAccount) {
        const isRoomRev = (selectedAccount.name || '').toLowerCase().includes('room revenue')
        const isExpense = selectedAccount.type === 'Expenses'
        const isRevenue = selectedAccount.type === 'Revenue'
        
        if (isRoomRev) {
          const { data: hrs } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to)
          ;(hrs || []).forEach(r => {
            if (Number(r.room_revenue_usd) > 0) {
              combined.push({ id: `hrs-${r.id}`, entry_date: r.stat_date, description: 'Daily Room Revenue', currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.room_revenue_usd })
            }
          })
        }
        
        if (isExpense) {
          const { data: hee } = await supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('account_id', accountId).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
          ;(hee || []).forEach(r => {
            combined.push({ id: `hee-${r.id}`, entry_date: r.expense_date, description: r.notes || 'Expense Entry', currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          })
        }
        
        if (isRevenue && !isRoomRev) {
          const { data: hre } = await supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('account_id', accountId).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to)
          ;(hre || []).forEach(r => {
            combined.push({ id: `hre-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Revenue', currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          })
        }
        
        // F&B Revenue injection
        if (selectedAccount.code && selectedAccount.code.startsWith('41')) {
          const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
          ;(rdr || []).forEach(r => {
            let amount = 0
            if ((selectedAccount.name || '').toLowerCase().includes('food')) amount = Number(r.food_amount_usd) || 0
            else if ((selectedAccount.name || '').toLowerCase().includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
            else if ((selectedAccount.name || '').toLowerCase().includes('other')) amount = Number(r.other_amount_usd) || 0
            else amount = Number(r.total_amount_usd) || 0
            
            if (amount > 0) {
              combined.push({ id: `rdr-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Revenue`, currency: 'USD', debit_usd: 0, credit_usd: amount })
            }
          })
        }
        
        // Guest Invoices (Accounts Receivable) - AR is typically an Asset account. 
        if ((selectedAccount.name || '').toLowerCase().includes('accounts receivable') || (selectedAccount.name || '').toLowerCase().includes('guest ledger')) {
          const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
          ;(hgi || []).forEach(i => {
            if (Number(i.invoice_amount_usd) > 0) {
              combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: i.invoice_amount_usd, credit_usd: 0 })
            }
            if (Number(i.collected_amount_usd) > 0) {
              combined.push({ id: `hgi-col-${i.id}`, entry_date: i.invoice_date, description: `Payment Collected - ${(i.invoice_number || '').substring(0,8)}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: i.collected_amount_usd })
            }
          })
        }
      }
      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }
    
    setEntries(combined)
  }

  async function handleDelete(entry) {
    if (!confirm('Delete this ledger entry? This cannot be undone.')) return
    const { error } = await supabase.from('ledger_entries').delete().eq('id', entry.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadEntries()
  }

  async function generateLedgerReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const account = (accounts || []).find(a => a.id === selections.account)
    const { data } = await supabase.from('ledger_entries').select('*').eq('company_id', activeCompany.id).eq('account_id', selections.account)
      .gte('entry_date', range.from).lte('entry_date', range.to).order('entry_date')

    let combined = data || []
    
    // CAPITAL & LOANS
    if (account) {
      const isEqCont = ((account.name || '').toLowerCase().includes('contribution') || (account.name || '').toLowerCase().includes('equity')) && account.type === 'Equity'
      const isEqDiv = ((account.name || '').toLowerCase().includes('dividend') || (account.name || '').toLowerCase().includes('draw') || (account.name || '').toLowerCase().includes('retained')) && account.type === 'Equity'
      const isCash = (account.name || '').toLowerCase().includes('cash on hand') || (account.name || '').toLowerCase().includes('cash')
      
      const [{ data: oCont }, { data: oDiv }, { data: lTake }, { data: lRepay }] = await Promise.all([
        supabase.from('owner_contributions').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('loans_taken').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('loan_principal_payments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to)
      ])
      
      ;(oCont || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (isEqCont) combined.push({ id: `oc-eq-${r.id}`, entry_date: r.payment_date, description: `Owner Contribution: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          if (isCash) combined.push({ id: `oc-c-${r.id}`, entry_date: r.payment_date, description: `Owner Contribution: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        }
      })
      
      ;(oDiv || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (isEqDiv) combined.push({ id: `od-eq-${r.id}`, entry_date: r.payment_date, description: `Owner Dividend: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          if (isCash) combined.push({ id: `od-c-${r.id}`, entry_date: r.payment_date, description: `Owner Dividend: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        }
      })
      
      ;(lTake || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (account.id === r.loan_account_id) combined.push({ id: `lt-l-${r.id}`, entry_date: r.payment_date, description: `Loan Taken: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          if ((r.cash_account_id && account.id === r.cash_account_id) || (!r.cash_account_id && isCash)) combined.push({ id: `lt-c-${r.id}`, entry_date: r.payment_date, description: `Loan Taken: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        }
      })
      
      ;(lRepay || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (account.id === r.loan_account_id) combined.push({ id: `lr-l-${r.id}`, entry_date: r.payment_date, description: `Loan Repayment: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          if ((r.cash_account_id && account.id === r.cash_account_id) || (!r.cash_account_id && isCash)) combined.push({ id: `lr-c-${r.id}`, entry_date: r.payment_date, description: `Loan Repayment: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        }
      })
      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }
    
    if (['hotel', 'restaurant'].includes(activeProduct) && account) {
      const isRoomRev = (account.name || '').toLowerCase().includes('room revenue')
      const isExpense = account.type === 'Expenses'
      const isRevenue = account.type === 'Revenue'
      
      if (isRoomRev) {
        const { data: hrs } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to)
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) {
            combined.push({ id: `hrs-${r.id}`, entry_date: r.stat_date, description: 'Daily Room Revenue', currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.room_revenue_usd })
          }
        })
      }
      
      if (isExpense) {
        const { data: hee } = await supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('account_id', account.id).gte('expense_date', range.from).lte('expense_date', range.to)
        ;(hee || []).forEach(r => {
          combined.push({ id: `hee-${r.id}`, entry_date: r.expense_date, description: r.notes || 'Expense Entry', currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        })
      }
      
      if (isRevenue && !isRoomRev) {
        const { data: hre } = await supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('account_id', account.id).gte('entry_date', range.from).lte('entry_date', range.to)
        ;(hre || []).forEach(r => {
          combined.push({ id: `hre-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Revenue', currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        })
      }
      
      if (account.code && account.code.startsWith('41')) {
        const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)
        ;(rdr || []).forEach(r => {
          let amount = 0
          if ((account.name || '').toLowerCase().includes('food')) amount = Number(r.food_amount_usd) || 0
          else if ((account.name || '').toLowerCase().includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
          else if ((account.name || '').toLowerCase().includes('other')) amount = Number(r.other_amount_usd) || 0
          else amount = Number(r.total_amount_usd) || 0
          
          if (amount > 0) {
            combined.push({ id: `rdr-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Revenue`, currency: 'USD', debit_usd: 0, credit_usd: amount })
          }
        })
      }
      
      if ((account.name || '').toLowerCase().includes('accounts receivable') || (account.name || '').toLowerCase().includes('guest ledger')) {
        const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
        ;(hgi || []).forEach(i => {
          if (Number(i.invoice_amount_usd) > 0) {
            combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: i.invoice_amount_usd, credit_usd: 0 })
          }
          if (Number(i.collected_amount_usd) > 0) {
            combined.push({ id: `hgi-col-${i.id}`, entry_date: i.invoice_date, description: `Payment Collected - ${(i.invoice_number || '').substring(0,8)}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: i.collected_amount_usd })
          }
        })
      }
      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }

    let running = 0
    const rows = combined.map(e => {
      running += Number(e.debit_usd) - Number(e.credit_usd)
      const balStr = running < 0 ? `${fmt(Math.abs(running))} Cr` : (running > 0 ? `${fmt(running)} Dr` : fmt(0)); return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', balStr]
    })
    const totalDebit = (data || []).reduce((s, e) => s + Number(e.debit_usd), 0)
    const totalCredit = (data || []).reduce((s, e) => s + Number(e.credit_usd), 0)

    const sections = [{
      heading: account ? `${account.code} - ${account.name}` : 'Account Ledger',
      columns: ['Date', 'Description', 'Orig. Currency', `Debit (${selections.currency})`, `Credit (${selections.currency})`, `Balance (${selections.currency})`],
      rows,
    }, {
      heading: 'Totals',
      keyValuePairs: [[`Total Debit (${selections.currency})`, fmt(totalDebit)], [`Total Credit (${selections.currency})`, fmt(totalCredit)]],
    }]

    const title = 'Account Ledger'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'account_ledger_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'account_ledger_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'account_ledger_report' })
  }

  if (!activeCompany) return null

  let running = 0
  const withBalance = entries.map(e => {
    running += Number(e.debit_usd) - Number(e.credit_usd)
    return { ...e, balance: running }
  })
  const totalDebit = entries.reduce((s, e) => s + Number(e.debit_usd), 0)
  const totalCredit = entries.reduce((s, e) => s + Number(e.credit_usd), 0)

  return (
    <div>
      <PageHeader
        title="Account Ledger"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 mb-5 grid sm:grid-cols-3 gap-3">
        <div>
          <label className="text-xs font-medium text-slate-500">Select Account</label>
          <select value={accountId} onChange={e => setAccountId(e.target.value)}
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            {accounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">From Date</label>
          <input type="date" value={cp.periodProps.customFrom || cp.range.from} onChange={e => cp.periodProps.onCustomChange({ from: e.target.value, to: cp.range.to })}
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">To Date</label>
          <input type="date" value={cp.periodProps.customTo || cp.range.to} onChange={e => cp.periodProps.onCustomChange({ from: cp.range.from, to: e.target.value })}
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </div>
      </div>

      <DataTable
        columns={[
          { key: 'entry_date', label: 'Date' },
          { key: 'description', label: 'Description' },
          { key: 'currency', label: 'Orig. Currency' },
          { key: 'debit_usd', label: `Debit (${cp.displayCurrency})`, render: r => Number(r.debit_usd) ? cp.fmt(r.debit_usd) : '—' },
          { key: 'credit_usd', label: `Credit (${cp.displayCurrency})`, render: r => Number(r.credit_usd) ? cp.fmt(r.credit_usd) : '—' },
          { key: 'balance', label: `Balance (${cp.displayCurrency})`, render: r => r.balance < 0 ? `${cp.fmt(Math.abs(r.balance))} Cr` : (r.balance > 0 ? `${cp.fmt(r.balance)} Dr` : cp.fmt(0)) },
          ...(can(['owner', 'admin', 'accountant']) ? [{
            key: 'actions', label: '', render: r => (
              <button onClick={() => handleDelete(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
            )
          }] : []),
        ]}
        rows={withBalance}
        emptyMessage="No ledger entries in this range."
      />

      {entries.length > 0 && (
        <div className="flex justify-end gap-8 mt-4 px-2 text-sm font-semibold text-slate-600">
          <span>Total Debit: {cp.fmt(totalDebit)}</span>
          <span>Total Credit: {cp.fmt(totalCredit)}</span>
        </div>
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Account Ledger"
          fields={[
            { type: 'select', key: 'account', label: 'Account', options: accounts.map(a => ({ value: a.id, label: `${a.code} - ${a.name}` })), default: accountId },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateLedgerReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
