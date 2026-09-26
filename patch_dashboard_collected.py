with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

old_collected = """    // Collected = Guest Invoices Paid + Daily Room Revenue Collected
    const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.collected_usd || r.amount_usd || 0), 0)
    const restRevCollected = restaurantRevenue.reduce((s, r) => s + Number(r.collected_usd || 0), 0)
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected + restRevCollected"""

new_collected = """    // Collected = Room Revenue Collected + Ancillary Collected + Restaurant Collected
    const roomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.collected_usd || 0), 0)
    const restRevCollected = restaurantRevenue.reduce((s, r) => s + Number(r.collected_usd || 0), 0)
    collected = roomCollected + ancillaryCollected + restRevCollected"""

content = content.replace(old_collected, new_collected)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
