import re

with open('src/pages/PortfolioDashboard.jsx', 'r') as f:
    code = f.read()

# Add hotel metrics query
old_query = """  async function computeCompanyProductMetrics(companyId, product, range) {
    const [{ data: accounts }, { data: entries }, { data: salesInv }, { data: receipts }] = await Promise.all(["""
new_query = """  async function computeCompanyProductMetrics(companyId, product, range) {
    const [{ data: accounts }, { data: entries }, { data: salesInv }, { data: receipts }, { data: hotelSettings }, { data: hotelStats }] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', companyId).eq('product', product).maybeSingle(),
      product === 'hotel' ? supabase.from('hotel_room_stats').select('rooms_occupied, room_revenue_usd').eq('company_id', companyId).eq('product', product).gte('stat_date', range.from).lte('stat_date', range.to) : Promise.resolve({ data: null }),"""

code = code.replace(old_query, new_query)

# Add logic for hotel stats
old_logic = """    return {
      revenue, expense, profit: revenue - expense,
      invoices,
      collected,
    }
  }"""
new_logic = """    let hotelKPIs = null
    if (product === 'hotel') {
      const totalRooms = hotelSettings?.total_rooms || 0
      const daysInView = Math.max(1, Math.round((new Date(range.to) - new Date(range.from)) / (1000 * 60 * 60 * 24)) + 1)
      const availableRoomNights = totalRooms * daysInView
      const totalOccupied = (hotelStats || []).reduce((s, r) => s + (r.rooms_occupied || 0), 0)
      const totalRoomRevenue = (hotelStats || []).reduce((s, r) => s + Number(r.room_revenue_usd || 0), 0)
      
      const occPct = availableRoomNights > 0 ? (totalOccupied / availableRoomNights) * 100 : 0
      const adr = totalOccupied > 0 ? totalRoomRevenue / totalOccupied : 0
      const revpar = availableRoomNights > 0 ? totalRoomRevenue / availableRoomNights : 0
      hotelKPIs = { occPct, adr, revpar }
    }

    return {
      revenue, expense, profit: revenue - expense,
      invoices,
      collected,
      hotelKPIs
    }
  }"""
code = code.replace(old_logic, new_logic)

# Show hotel KPIs in the company card
old_card = """                        <div className="flex justify-between items-center text-sm">
                          <span className="text-slate-500">Expense</span>
                          <span className="font-medium text-slate-700">{cp.fmt(pMetrics.expense)}</span>
                        </div>
                      </div>
                    </div>"""
new_card = """                        <div className="flex justify-between items-center text-sm">
                          <span className="text-slate-500">Expense</span>
                          <span className="font-medium text-slate-700">{cp.fmt(pMetrics.expense)}</span>
                        </div>
                        {pMetrics.hotelKPIs && (
                          <div className="pt-3 border-t border-slate-100 grid grid-cols-3 gap-2">
                            <div>
                              <div className="text-[10px] text-slate-400 uppercase tracking-wide">Occ %</div>
                              <div className="font-semibold text-slate-700 text-sm">{pMetrics.hotelKPIs.occPct.toFixed(1)}%</div>
                            </div>
                            <div>
                              <div className="text-[10px] text-slate-400 uppercase tracking-wide">ADR</div>
                              <div className="font-semibold text-slate-700 text-sm">{cp.fmt(pMetrics.hotelKPIs.adr)}</div>
                            </div>
                            <div>
                              <div className="text-[10px] text-slate-400 uppercase tracking-wide">RevPAR</div>
                              <div className="font-semibold text-slate-700 text-sm">{cp.fmt(pMetrics.hotelKPIs.revpar)}</div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>"""
code = code.replace(old_card, new_card)

with open('src/pages/PortfolioDashboard.jsx', 'w') as f:
    f.write(code)
