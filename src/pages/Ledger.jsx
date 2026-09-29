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
      
    const ignoredSources = ['restaurant_revenue', 'hotel_room_stats', 'hotel_revenue_entry', 'hotel_expense_entry', 'hotel_amc', 'hotel_guest_invoice', 'owner_contribution', 'owner_dividend', 'loan_taken', 'loan_principal']
    const filteredEntries = (data || []).filter(e => {
      if (['hotel', 'restaurant'].includes(activeProduct)) {
        return !ignoredSources.includes(e.source_type)
      }
      return true
    })
    let combined = [...filteredEntries]
    
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
        if (selectedAccount.code && (selectedAccount.code.startsWith('41') || selectedAccount.code.startsWith('40'))) {
          const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
          ;(rdr || []).forEach(r => {
            const meal = (r.meal_period || '').toLowerCase()
            const mealAcc = meal ? (accounts || []).find(a => (a.name || '').toLowerCase().includes(meal) && a.type === 'Revenue') : null
            
            let amount = 0
            if (mealAcc) {
              // If a dedicated meal account exists, ALL revenue goes there
              if (selectedAccount.id === mealAcc.id) {
                amount = (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0)
              }
            } else {
              // Otherwise it splits by category
              const accName = (selectedAccount.name || '').toLowerCase()
              if (accName.includes('food')) amount = Number(r.food_amount_usd) || 0
              else if (accName.includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
              else if (accName.includes('other')) amount = Number(r.other_amount_usd) || 0
            }
            
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
        // CASH & AR INJECTION (Hotel/Restaurant specific)
        const isCash = (selectedAccount.name || '').toLowerCase().includes('cash on hand') || (selectedAccount.name || '').toLowerCase().includes('cash')
        const isAr = (selectedAccount.name || '').toLowerCase().includes('accounts receivable') || (selectedAccount.name || '').toLowerCase().includes('guest ledger')
        
        if (isCash || isAr) {
          const [{ data: hrs }, { data: rdr }, { data: hre }, { data: hee }, { data: amc }, { data: hgi }] = await Promise.all([
            supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to),
            supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to),
            supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
            supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to),
            supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
            supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
          ])
          
          if (isCash) {
            ;(hrs || []).forEach(r => {
               const col = Number(r.manual_room_revenue_collected_usd) || Number(r.room_revenue_usd) || 0
               if (col > 0) combined.push({ id: `hrs-c-${r.id}`, entry_date: r.stat_date, description: 'Room Revenue Collected', currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               if (col > 0) combined.push({ id: `rdr-c-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Collected`, currency: 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(hre || []).forEach(r => {
               const col = Number(r.collected_usd) || Number(r.amount_usd) || 0
               if (col > 0) combined.push({ id: `hre-c-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Collected', currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(hee || []).forEach(r => {
               const amt = Number(r.amount_usd) || 0
               if (amt > 0) combined.push({ id: `hee-c-${r.id}`, entry_date: r.expense_date, description: r.notes || 'Expense Paid', currency: r.currency || 'USD', debit_usd: 0, credit_usd: amt })
            })
            if (amc && amc.length > 0) {
              const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
              if (amcMonthly > 0) {
                const start = new Date(cp.range.from < '2020-01-01' ? '2020-01-01' : cp.range.from)
                const end = new Date(cp.range.to)
                let cur = new Date(start.getFullYear(), start.getMonth(), 1)
                while (cur <= end) {
                  const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
                  combined.push({ id: `amc-c-${dStr}`, entry_date: dStr, description: 'AMC Monthly Amortization', currency: 'USD', debit_usd: 0, credit_usd: amcMonthly })
                  cur.setMonth(cur.getMonth() + 1)
                }
              }
            }
            ;(hgi || []).forEach(r => {
               const col = Number(r.collected_amount_usd) || 0
               if (col > 0) combined.push({ id: `hgi-c-${r.id}`, entry_date: r.invoice_date, description: `Invoice Collected: ${(r.invoice_number||'').substring(0,8)}`, currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
          }
          
          if (isAr) {
            ;(hrs || []).forEach(r => {
               const rev = Number(r.room_revenue_usd) || 0
               const col = Number(r.manual_room_revenue_collected_usd) || rev
               const uncol = Math.max(0, rev - col)
               if (uncol > 0) combined.push({ id: `hrs-ar-${r.id}`, entry_date: r.stat_date, description: 'Room Revenue Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               const uncol = Math.max(0, total - col)
               if (uncol > 0) combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Uncollected`, currency: 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            ;(hre || []).forEach(r => {
               const rev = Number(r.amount_usd) || 0
               const col = Number(r.collected_usd) || rev
               const uncol = Math.max(0, rev - col)
               if (uncol > 0) combined.push({ id: `hre-ar-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            // hgi is already partially handled by the block above it, but we can safely remove the old hgi block and rely entirely on this new AR block!
            // Wait, I will just let the old hgi block stay, but modify my new AR block to NOT include hgi, to avoid double counting!
            // Actually, the old hgi block does: debit_usd: i.invoice_amount_usd, credit_usd: 0 (for invoice). And credit_usd: i.collected_amount_usd (for collection).
            // That is mathematically perfect for AR! So we skip hgi here.
          }
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

    const ignoredSources = ['restaurant_revenue', 'hotel_room_stats', 'hotel_revenue_entry', 'hotel_expense_entry', 'hotel_amc', 'hotel_guest_invoice', 'owner_contribution', 'owner_dividend', 'loan_taken', 'loan_principal']
    const filteredEntries = (data || []).filter(e => {
      if (['hotel', 'restaurant'].includes(activeProduct)) {
        return !ignoredSources.includes(e.source_type)
      }
      return true
    })
    let combined = [...filteredEntries]
    
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
      
      if (account.code && (account.code.startsWith('41') || account.code.startsWith('40'))) {
        const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)
        ;(rdr || []).forEach(r => {
          const meal = (r.meal_period || '').toLowerCase()
          const mealAcc = meal ? (accounts || []).find(a => (a.name || '').toLowerCase().includes(meal) && a.type === 'Revenue') : null
          
          let amount = 0
          if (mealAcc) {
            if (account.id === mealAcc.id) {
              amount = (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0)
            }
          } else {
            const accName = (account.name || '').toLowerCase()
            if (accName.includes('food')) amount = Number(r.food_amount_usd) || 0
            else if (accName.includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
            else if (accName.includes('other')) amount = Number(r.other_amount_usd) || 0
          }
          
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
        // CASH & AR INJECTION (Hotel/Restaurant specific)
        const isCash = (account.name || '').toLowerCase().includes('cash on hand') || (account.name || '').toLowerCase().includes('cash')
        const isAr = (account.name || '').toLowerCase().includes('accounts receivable') || (account.name || '').toLowerCase().includes('guest ledger')
        
        if (isCash || isAr) {
          const [{ data: hrs }, { data: rdr }, { data: hre }, { data: hee }, { data: amc }, { data: hgi }] = await Promise.all([
            supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to),
            supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to),
            supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to),
            supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to),
            supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
            supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
          ])
          
          if (isCash) {
            ;(hrs || []).forEach(r => {
               const col = Number(r.manual_room_revenue_collected_usd) || Number(r.room_revenue_usd) || 0
               if (col > 0) combined.push({ id: `hrs-c-${r.id}`, entry_date: r.stat_date, description: 'Room Revenue Collected', currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               if (col > 0) combined.push({ id: `rdr-c-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Collected`, currency: 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(hre || []).forEach(r => {
               const col = Number(r.collected_usd) || Number(r.amount_usd) || 0
               if (col > 0) combined.push({ id: `hre-c-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Collected', currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(hee || []).forEach(r => {
               const amt = Number(r.amount_usd) || 0
               if (amt > 0) combined.push({ id: `hee-c-${r.id}`, entry_date: r.expense_date, description: r.notes || 'Expense Paid', currency: r.currency || 'USD', debit_usd: 0, credit_usd: amt })
            })
            if (amc && amc.length > 0) {
              const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
              if (amcMonthly > 0) {
                const start = new Date(range.from < '2020-01-01' ? '2020-01-01' : range.from)
                const end = new Date(range.to)
                let cur = new Date(start.getFullYear(), start.getMonth(), 1)
                while (cur <= end) {
                  const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
                  combined.push({ id: `amc-c-${dStr}`, entry_date: dStr, description: 'AMC Monthly Amortization', currency: 'USD', debit_usd: 0, credit_usd: amcMonthly })
                  cur.setMonth(cur.getMonth() + 1)
                }
              }
            }
            ;(hgi || []).forEach(r => {
               const col = Number(r.collected_amount_usd) || 0
               if (col > 0) combined.push({ id: `hgi-c-${r.id}`, entry_date: r.invoice_date, description: `Invoice Collected: ${(r.invoice_number||'').substring(0,8)}`, currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
          }
          
          if (isAr) {
            ;(hrs || []).forEach(r => {
               const rev = Number(r.room_revenue_usd) || 0
               const col = Number(r.manual_room_revenue_collected_usd) || rev
               const uncol = Math.max(0, rev - col)
               if (uncol > 0) combined.push({ id: `hrs-ar-${r.id}`, entry_date: r.stat_date, description: 'Room Revenue Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               const uncol = Math.max(0, total - col)
               if (uncol > 0) combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Uncollected`, currency: 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            ;(hre || []).forEach(r => {
               const rev = Number(r.amount_usd) || 0
               const col = Number(r.collected_usd) || rev
               const uncol = Math.max(0, rev - col)
               if (uncol > 0) combined.push({ id: `hre-ar-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            // hgi is already partially handled by the block above it, but we can safely remove the old hgi block and rely entirely on this new AR block!
            // Wait, I will just let the old hgi block stay, but modify my new AR block to NOT include hgi, to avoid double counting!
            // Actually, the old hgi block does: debit_usd: i.invoice_amount_usd, credit_usd: 0 (for invoice). And credit_usd: i.collected_amount_usd (for collection).
            // That is mathematically perfect for AR! So we skip hgi here.
          }
        }

      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }

    const rows = combined.map(e => {
      const lineBalance = Number(e.debit_usd) - Number(e.credit_usd)
      const balStr = lineBalance < 0 ? `-${fmt(Math.abs(lineBalance))}` : fmt(lineBalance); 
      return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', balStr]
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

  const withBalance = entries.map(e => {
    return { ...e, balance: Number(e.debit_usd) - Number(e.credit_usd) }
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
          { key: 'balance', label: `Balance (${cp.displayCurrency})`, render: r => r.balance < 0 ? `-${cp.fmt(Math.abs(r.balance))}` : cp.fmt(r.balance) },
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
