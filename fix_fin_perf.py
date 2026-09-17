import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    code = f.read()

old_fin = """  async function loadAll() {
    setLoading(true)
    const [{ data: sales }, { data: purchases }, { data: led }] = await Promise.all([
      supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
    ])"""

new_fin = """  async function loadAll() {
    setLoading(true)
    const [{ data: led }] = await Promise.all([
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
    ])
    // Synthesize total sales/purchases from ledger to ensure universal accuracy across all products
    const sales = led.filter(l => l.accounts?.type === 'Revenue' && Number(l.credit_usd) > 0).map(l => ({ amount_usd: l.credit_usd }))
    const purchases = led.filter(l => l.accounts?.type === 'Expenses' && Number(l.debit_usd) > 0).map(l => ({ amount_usd: l.debit_usd }))"""
code = code.replace(old_fin, new_fin)

old_pdf = """  async function generatePerformanceReport(selections, format) {
    const range = resolveReportPeriod(selections.period)
    const [{ data: sales }, { data: purchases }, { data: led }] = await Promise.all([
      supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to),
    ])"""
new_pdf = """  async function generatePerformanceReport(selections, format) {
    const range = resolveReportPeriod(selections.period)
    const [{ data: led }] = await Promise.all([
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to),
    ])
    const sales = led.filter(l => l.accounts?.type === 'Revenue' && Number(l.credit_usd) > 0).map(l => ({ amount_usd: l.credit_usd }))
    const purchases = led.filter(l => l.accounts?.type === 'Expenses' && Number(l.debit_usd) > 0).map(l => ({ amount_usd: l.debit_usd }))"""
code = code.replace(old_pdf, new_pdf)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(code)
