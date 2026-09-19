import re

with open('src/pages/Analytics.jsx', 'r') as f:
    code = f.read()

old_logic = """    const totalInvoiced = sSel.reduce((s2, i) => s2 + Number(i.amount_usd), 0)
    const outstanding = sSel.reduce((s2, i) => s2 + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    const collected = totalInvoiced - outstanding
    const expenses = pSel.reduce((s2, i) => s2 + Number(i.amount_usd), 0)

    const monthlyMap = {}
    sSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.amount_usd) })
    rSel.forEach(i => { const k = i.receipt_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].collected += Number(i.amount_usd) })
    const monthlySel = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))"""

new_logic = """    let totalInvoiced = 0
    let outstanding = 0
    let collected = 0
    let expenses = 0
    const monthlyMap = {}

    if (activeProduct === 'hotel') {
      const manualRoomCollected = hrsSel.reduce((s2, r) => s2 + Number(r.manual_room_revenue_collected_usd || 0), 0)
      const manualRoomRevenue = hrsSel.reduce((s2, r) => s2 + Number(r.room_revenue_usd || 0), 0)
      const guestInvoiceCollected = hgiSel.reduce((s2, i) => s2 + Number(i.collected_amount_usd || 0), 0)
      const guestInvoiceRevenue = hgiSel.reduce((s2, i) => s2 + Number(i.invoice_amount_usd || 0), 0)
      const ancillaryCollected = hreSel.reduce((s2, r) => s2 + Number(r.amount_usd || 0), 0)

      totalInvoiced = manualRoomRevenue + guestInvoiceRevenue + ancillaryCollected
      collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected
      outstanding = hgiSel.reduce((s2, i) => s2 + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)

      const start = new Date(range.from)
      const end = new Date(Math.min(new Date(range.to).getTime(), new Date().getTime()))
      const monthsInView = Math.max(1, (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1)
      const amcTotal = hamcSel.reduce((s2, r) => s2 + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
      expenses = heeSel.reduce((s2, e) => s2 + Number(e.amount_usd), 0) + amcTotal

      hgiSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.invoice_amount_usd || 0); monthlyMap[k].collected += Number(i.collected_amount_usd || 0) })
      hrsSel.forEach(i => { const k = i.stat_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.room_revenue_usd || 0); monthlyMap[k].collected += Number(i.manual_room_revenue_collected_usd || 0) })
      hreSel.forEach(i => { const k = i.entry_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.amount_usd || 0); monthlyMap[k].collected += Number(i.amount_usd || 0) })

    } else {
      totalInvoiced = sSel.reduce((s2, i) => s2 + Number(i.amount_usd), 0)
      outstanding = sSel.reduce((s2, i) => s2 + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
      collected = totalInvoiced - outstanding
      expenses = pSel.reduce((s2, i) => s2 + Number(i.amount_usd), 0)

      sSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.amount_usd) })
      rSel.forEach(i => { const k = i.receipt_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].collected += Number(i.amount_usd) })
    }

    const monthlySel = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))"""

code = code.replace(old_logic, new_logic)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(code)
