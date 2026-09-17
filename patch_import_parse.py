import re

with open('src/pages/HistoricalImport.jsx', 'r') as f:
    code = f.read()

old_parse = """  function handleHotelFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setHotelFileName(file.name)
    setHotelResult(null)
    const reader = new FileReader()
    reader.onload = (evt) => {
      const wb = XLSX.read(evt.target.result, { type: 'array' })
      const errors = []
      const actuals = []
      const budgetRows = []

      const actualsSheet = wb.Sheets['Room Revenue Actuals']
      if (actualsSheet) {
        const rows = XLSX.utils.sheet_to_json(actualsSheet, { header: 1, raw: false }).slice(1)
        rows.forEach((row, i) => {
          const [dateRaw, occRaw, revRaw, collectedRaw, currencyRaw] = row
          if (!dateRaw && !occRaw && !revRaw) return
          const date = normalizeDate(dateRaw)
          if (!date) { errors.push(`Room Revenue Actuals row ${i + 2}: invalid date.`); return }
          const revenue = parseFloat(revRaw)
          if (!revenue || revenue <= 0) { errors.push(`Room Revenue Actuals row ${i + 2}: Room Revenue must be a positive number.`); return }
          actuals.push({
            date, roomsOccupied: parseInt(occRaw) || 0, revenue,
            collected: parseFloat(collectedRaw) || revenue,
            currency: String(currencyRaw || 'USD').trim().toUpperCase() || 'USD',
          })
        })
      }

      const budgetSheet = wb.Sheets['Room Revenue Budget']
      if (budgetSheet) {
        const rows = XLSX.utils.sheet_to_json(budgetSheet, { header: 1, raw: false }).slice(1)
        rows.forEach((row, i) => {
          const [yearRaw, monthRaw, occRaw, adrRaw, revRaw, currencyRaw] = row
          if (!yearRaw && !monthRaw && !revRaw) return
          const year = parseInt(yearRaw), month = parseInt(monthRaw)
          if (!year || !month || month < 1 || month > 12) { errors.push(`Room Revenue Budget row ${i + 2}: invalid year/month.`); return }
          budgetRows.push({
            year, month, occ: parseFloat(occRaw) || 0, adr: parseFloat(adrRaw) || 0, revenue: parseFloat(revRaw) || 0,
            currency: String(currencyRaw || 'USD').trim().toUpperCase() || 'USD',
          })
        })
      }

      if (errors.length > 0) {
        setHotelErrors(errors.slice(0, 10))
        setHotelParsedActuals([]); setHotelParsedBudget([])
      } else {
        setHotelErrors([])
        setHotelParsedActuals(actuals)
        setHotelParsedBudget(budgetRows)
      }
    }
    reader.readAsArrayBuffer(file)
  }

  async function handleHotelImport() {
    setHotelImporting(true)
    setHotelResult(null)
    setHotelErrors([])
    try {
      const rateCache = { USD: 1 }
      const rateFor = async (c) => { if (!(c in rateCache)) rateCache[c] = (await getLatestRate(c)) || 1; return rateCache[c] }

      for (const row of hotelParsedActuals) {
        const rate = await rateFor(row.currency)
        await supabase.from('hotel_room_stats').upsert({
          company_id: activeCompany.id, product: activeProduct, stat_date: row.date, rooms_occupied: row.roomsOccupied,
          currency: row.currency, fx_rate_locked: rate,
          room_revenue: row.revenue, room_revenue_collected: row.collected,
          room_revenue_usd: Math.round(row.revenue / rate * 100) / 100,
          room_revenue_collected_usd: Math.round(row.collected / rate * 100) / 100,
        }, { onConflict: 'company_id,product,stat_date' })
      }

      for (const row of hotelParsedBudget) {
        const rate = await rateFor(row.currency)
        await supabase.from('hotel_room_revenue_budget').upsert({
          company_id: activeCompany.id, product: activeProduct, budget_year: row.year, budget_month: row.month,
          budgeted_occupancy_pct: row.occ, budgeted_adr: row.adr, budgeted_room_revenue: row.revenue,
          currency: row.currency, fx_rate_locked: rate, budgeted_room_revenue_usd: Math.round(row.revenue / rate * 100) / 100,
        }, { onConflict: 'company_id,product,budget_year,budget_month' })
      }

      setHotelResult({ success: true, actualsCount: hotelParsedActuals.length, budgetCount: hotelParsedBudget.length })
      setHotelParsedActuals([]); setHotelParsedBudget([]); setHotelErrors([]); setHotelFileName('')
      if (hotelFileInputRef.current) hotelFileInputRef.current.value = ''
    } catch (err) {
      setHotelResult({ success: false, message: err.message })
    } finally {
      setHotelImporting(false)
    }
  }"""

new_parse = """  const [hotelParsedInvoices, setHotelParsedInvoices] = useState([])
  const [hotelParsedExpenses, setHotelParsedExpenses] = useState([])

  function handleHotelFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setHotelFileName(file.name)
    setHotelResult(null)
    const reader = new FileReader()
    reader.onload = (evt) => {
      const wb = XLSX.read(evt.target.result, { type: 'array' })
      const errors = []
      const invoices = []
      const actuals = []
      const expenses = []
      const budgetRows = []

      // Parse Guest Invoices
      const giSheet = wb.Sheets['Guest Invoices']
      if (giSheet) {
        const rows = XLSX.utils.sheet_to_json(giSheet, { header: 1, raw: false }).slice(1)
        rows.forEach((row, i) => {
          const [dateRaw, room, guest, checkin, checkout, rate, nights, otherCode, otherAmt, curr, col] = row
          if (!dateRaw && !guest) return
          const date = normalizeDate(dateRaw)
          if (!date) { errors.push(`Guest Invoices row ${i + 2}: invalid date.`); return }
          let lineItems = []
          if (otherCode && otherAmt) {
             const acc = accounts.find(a => a.code === String(otherCode).trim())
             if (!acc) errors.push(`Guest Invoices row ${i + 2}: invalid account code ${otherCode}.`)
             else lineItems.push({ account_id: acc.id, amount: parseFloat(otherAmt) || 0, notes: '' })
          }
          const roomRate = parseFloat(rate) || 0; const nts = parseInt(nights) || 0;
          const otherRev = parseFloat(otherAmt) || 0;
          const totalInv = (roomRate * nts) + otherRev
          invoices.push({
            date, room: room ? String(room) : null, guest: String(guest), checkin: normalizeDate(checkin), checkout: normalizeDate(checkout),
            roomRate, nights: nts, roomRevenue: roomRate * nts, otherRevenue: otherRev, lineItems,
            currency: String(curr || 'USD').trim().toUpperCase(), invoiceAmount: totalInv, collected: parseFloat(col) || totalInv
          })
        })
      }

      // Parse Daily Revenue Manual
      const actualsSheet = wb.Sheets['Daily Revenue Manual'] || wb.Sheets['Room Revenue Actuals']
      if (actualsSheet) {
        const rows = XLSX.utils.sheet_to_json(actualsSheet, { header: 1, raw: false }).slice(1)
        rows.forEach((row, i) => {
          const [dateRaw, occRaw, revRaw, collectedRaw, currencyRaw] = row
          if (!dateRaw && !occRaw && !revRaw) return
          const date = normalizeDate(dateRaw)
          if (!date) { errors.push(`Daily Revenue row ${i + 2}: invalid date.`); return }
          const revenue = parseFloat(revRaw)
          if (!revenue || revenue <= 0) { errors.push(`Daily Revenue row ${i + 2}: Room Revenue must be positive.`); return }
          actuals.push({
            date, roomsOccupied: parseInt(occRaw) || 0, revenue,
            collected: parseFloat(collectedRaw) || revenue,
            currency: String(currencyRaw || 'USD').trim().toUpperCase() || 'USD',
          })
        })
      }

      // Parse Expenses
      const expSheet = wb.Sheets['Expenses']
      if (expSheet) {
        const rows = XLSX.utils.sheet_to_json(expSheet, { header: 1, raw: false }).slice(1)
        rows.forEach((row, i) => {
          const [dateRaw, codeRaw, amtRaw, currRaw, notes] = row
          if (!dateRaw && !amtRaw) return
          const date = normalizeDate(dateRaw)
          if (!date) { errors.push(`Expenses row ${i + 2}: invalid date.`); return }
          const acc = accounts.find(a => a.code === String(codeRaw).trim())
          if (!acc) { errors.push(`Expenses row ${i + 2}: invalid account code ${codeRaw}.`); return }
          expenses.push({
             date, accountId: acc.id, amount: parseFloat(amtRaw) || 0, currency: String(currRaw || 'USD').trim().toUpperCase(), notes: String(notes||'')
          })
        })
      }

      // Parse Budget
      const budgetSheet = wb.Sheets['Room Revenue Budget']
      if (budgetSheet) {
        const rows = XLSX.utils.sheet_to_json(budgetSheet, { header: 1, raw: false }).slice(1)
        rows.forEach((row, i) => {
          const [yearRaw, monthRaw, occRaw, adrRaw, revRaw, currencyRaw] = row
          if (!yearRaw && !monthRaw && !revRaw) return
          const year = parseInt(yearRaw), month = parseInt(monthRaw)
          if (!year || !month || month < 1 || month > 12) { errors.push(`Room Revenue Budget row ${i + 2}: invalid year/month.`); return }
          budgetRows.push({
            year, month, occ: parseFloat(occRaw) || 0, adr: parseFloat(adrRaw) || 0, revenue: parseFloat(revRaw) || 0,
            currency: String(currencyRaw || 'USD').trim().toUpperCase() || 'USD',
          })
        })
      }

      if (errors.length > 0) {
        setHotelErrors(errors.slice(0, 10))
        setHotelParsedActuals([]); setHotelParsedBudget([]); setHotelParsedInvoices([]); setHotelParsedExpenses([])
      } else {
        setHotelErrors([])
        setHotelParsedActuals(actuals)
        setHotelParsedBudget(budgetRows)
        setHotelParsedInvoices(invoices)
        setHotelParsedExpenses(expenses)
      }
    }
    reader.readAsArrayBuffer(file)
  }

  async function handleHotelImport() {
    setHotelImporting(true)
    setHotelResult(null)
    setHotelErrors([])
    try {
      const rateCache = { USD: 1 }
      const rateFor = async (c) => { if (!(c in rateCache)) rateCache[c] = (await getLatestRate(c)) || 1; return rateCache[c] }

      // 1. Invoices
      for (const row of hotelParsedInvoices) {
        const rate = await rateFor(row.currency)
        await supabase.from('hotel_guest_invoices').insert({
          company_id: activeCompany.id, product: activeProduct, invoice_date: row.date, room_number: row.room, guest_name: row.guest,
          checkin_date: row.checkin || null, checkout_date: row.checkout || null, room_rate: row.roomRate, nights: row.nights,
          room_revenue: row.roomRevenue, other_revenue: row.otherRevenue, line_items: row.lineItems,
          invoice_amount: row.invoiceAmount, collected_amount: row.collected, currency: row.currency, fx_rate_locked: rate,
          invoice_amount_usd: Math.round(row.invoiceAmount / rate * 100) / 100, collected_amount_usd: Math.round(row.collected / rate * 100) / 100
        })
      }

      // 2. Daily Manual
      for (const row of hotelParsedActuals) {
        const rate = await rateFor(row.currency)
        const roomRevUsd = Math.round(row.revenue / rate * 100) / 100
        // Because of the additive architecture, we MUST upsert and ADD to existing invoiced amounts, not overwrite
        // We use a small RPC or we can just fetch and add. Wait, the easiest is to fetch first, then upsert
        const { data: ext } = await supabase.from('hotel_room_stats').select('rooms_occupied, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('stat_date', row.date).maybeSingle()
        const extOcc = ext ? Number(ext.rooms_occupied) : 0
        const extRev = ext ? Number(ext.room_revenue_usd) : 0
        await supabase.from('hotel_room_stats').upsert({
          company_id: activeCompany.id, product: activeProduct, stat_date: row.date,
          rooms_occupied: extOcc + row.roomsOccupied, room_revenue_usd: extRev + roomRevUsd,
          room_revenue_collected_usd: extRev + roomRevUsd, currency: row.currency, fx_rate_locked: rate
        }, { onConflict: 'company_id,product,stat_date' })
      }

      // 3. Expenses
      for (const row of hotelParsedExpenses) {
        const rate = await rateFor(row.currency)
        await supabase.from('hotel_expense_entries').insert({
          company_id: activeCompany.id, product: activeProduct, expense_date: row.date, account_id: row.accountId,
          amount: row.amount, amount_usd: Math.round(row.amount / rate * 100) / 100, currency: row.currency, fx_rate_locked: rate,
          notes: row.notes || null, supplier_name: null
        })
      }

      // 4. Budget
      for (const row of hotelParsedBudget) {
        const rate = await rateFor(row.currency)
        await supabase.from('hotel_room_revenue_budget').upsert({
          company_id: activeCompany.id, product: activeProduct, budget_year: row.year, budget_month: row.month,
          budgeted_occupancy_pct: row.occ, budgeted_adr: row.adr, budgeted_room_revenue: row.revenue,
          currency: row.currency, fx_rate_locked: rate, budgeted_room_revenue_usd: Math.round(row.revenue / rate * 100) / 100,
        }, { onConflict: 'company_id,product,budget_year,budget_month' })
      }

      setHotelResult({ success: true, count: hotelParsedInvoices.length + hotelParsedActuals.length + hotelParsedExpenses.length + hotelParsedBudget.length })
      setHotelParsedActuals([]); setHotelParsedBudget([]); setHotelParsedInvoices([]); setHotelParsedExpenses([]); setHotelErrors([]); setHotelFileName('')
      if (hotelFileInputRef.current) hotelFileInputRef.current.value = ''
    } catch (err) {
      setHotelResult({ success: false, message: err.message })
    } finally {
      setHotelImporting(false)
    }
  }"""
code = code.replace(old_parse, new_parse)
with open('src/pages/HistoricalImport.jsx', 'w') as f: f.write(code)
