with open("src/pages/Dashboard.jsx", "r") as f:
    content = f.read()

replacement = """  let draftInvoices = [];
  if (['hotel', 'restaurant'].includes(activeProduct)) {
    const guestInvoices = hotelGuestInvoices.filter(i => Number(i.invoice_amount_usd) > Number(i.collected_amount_usd)).map(i => ({
        ...i,
        contact: { name: i.guest_name || 'Guest' },
        balance_due: Number(i.invoice_amount_usd) - Number(i.collected_amount_usd),
        amount: i.invoice_amount_usd,
        amount_usd: i.invoice_amount_usd,
        due_date: i.invoice_date,
        status: 'Pending',
        invoice_number: i.id ? i.id.slice(0, 8).toUpperCase() : '—'
    }));

    const uncollectedRooms = hotelRoomStats
        .filter(r => Number(r.room_revenue_usd || 0) > (Number(r.manual_room_revenue_collected_usd || 0) + Number(r.invoiced_room_revenue_collected || 0)))
        .map(r => {
            const bal = Number(r.room_revenue_usd || 0) - (Number(r.manual_room_revenue_collected_usd || 0) + Number(r.invoiced_room_revenue_collected || 0));
            return {
                invoice_number: 'ROOM REV',
                contact: { name: 'Daily Room Revenue' },
                due_date: r.stat_date,
                balance_due: bal,
                amount: bal,
                amount_usd: bal,
                currency: cp.displayCurrency,
                status: 'Uncollected'
            };
        });

    const uncollectedAncillary = hotelRevenueEntries
        .filter(r => Number(r.amount_usd || 0) > Number(r.collected_usd || 0))
        .map(r => {
            const bal = Number(r.amount_usd || 0) - Number(r.collected_usd || 0);
            return {
                invoice_number: 'ANC REV',
                contact: { name: r.account?.name || 'Ancillary Revenue' },
                due_date: r.entry_date,
                balance_due: bal,
                amount: bal,
                amount_usd: bal,
                currency: cp.displayCurrency,
                status: 'Uncollected'
            };
        });

    const uncollectedRestaurant = restaurantRevenue
        .filter(r => {
            const tot = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0));
            return tot > Number(r.collected_usd || 0);
        })
        .map(r => {
            const tot = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0));
            const bal = tot - Number(r.collected_usd || 0);
            return {
                invoice_number: 'F&B REV',
                contact: { name: r.meal_period + ' F&B Revenue' },
                due_date: r.revenue_date,
                balance_due: bal,
                amount: bal,
                amount_usd: bal,
                currency: cp.displayCurrency,
                status: 'Uncollected'
            };
        });

    draftInvoices = [...guestInvoices, ...uncollectedRooms, ...uncollectedAncillary, ...uncollectedRestaurant];
  } else {
    draftInvoices = sales.filter(i => i.status !== 'Paid');
  }

  const draftExpenses = activeProduct === 'hotel' ? [] : purchases.filter(i => i.status === 'Draft')"""

import re
content = re.sub(
    r"  const draftInvoices = \['hotel', 'restaurant'\].includes\(activeProduct\)[\s\S]*?const draftExpenses = activeProduct === 'hotel' \? \[\] : purchases\.filter\(i => i\.status === 'Draft'\)",
    replacement,
    content
)

with open("src/pages/Dashboard.jsx", "w") as f:
    f.write(content)

