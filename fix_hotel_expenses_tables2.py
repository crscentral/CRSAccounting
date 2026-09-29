import re

def main():
    with open('src/pages/HotelExpenses.jsx', 'r') as f:
        content = f.read()
        
    old_totals = "const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)"
    new_totals = """const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const hotelEntries = entries.filter(e => e.product === 'hotel')
  const restEntries = entries.filter(e => e.product === 'restaurant')
  const hotelAmc = amcContracts.filter(a => a.product === 'hotel')
  const restAmc = amcContracts.filter(a => a.product === 'restaurant')
  const hotelPI = purchaseInvoices.filter(p => p.product === 'hotel')
  const restPI = purchaseInvoices.filter(p => p.product === 'restaurant')
  
  const hotelEntriesTotal = hotelEntries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const restEntriesTotal = restEntries.reduce((s, r) => s + Number(r.amount_usd), 0)"""
  
    content = content.replace(old_totals, new_totals)

    # For the daily tab:
    match_daily = re.search(r"(\{activeTab === 'daily' && \(\n\s*<>\n\s*<div className=\"flex justify-between items-end mb-3\">.*?)(?=\{activeTab === 'purchase' && \()", content, re.DOTALL)
    if match_daily:
        old_daily = match_daily.group(1)
        hotel_daily = old_daily.replace("<span>Daily Expense Entries</span>", "<span>Hotel Daily Expense Entries</span>")
        hotel_daily = hotel_daily.replace("{cp.fmt(entriesTotalUsd)}", "{cp.fmt(hotelEntriesTotal)}")
        hotel_daily = hotel_daily.replace("entries.map(e => e.account_id)", "hotelEntries.map(e => e.account_id)")
        hotel_daily = hotel_daily.replace("rows={entries}", "rows={hotelEntries}")
        hotel_daily = hotel_daily.replace("AMC Contracts (auto-split across 12 months)", "Hotel AMC Contracts (auto-split across 12 months)")
        hotel_daily = hotel_daily.replace("rows={amcContracts}", "rows={hotelAmc}")
        
        # Remove the outer {activeTab === 'daily' && ( <> ... </> )} to append the restaurant part
        h_inner = hotel_daily.replace("{activeTab === 'daily' && (\n        <>\n", "")
        h_inner = h_inner.replace("        </>\n      )\n\n      ", "")
        
        r_inner = h_inner.replace("Hotel Daily Expense Entries", "Restaurant Daily Expense Entries")
        r_inner = r_inner.replace("hotelEntries", "restEntries")
        r_inner = r_inner.replace("hotelEntriesTotal", "restEntriesTotal")
        r_inner = r_inner.replace("Hotel AMC Contracts", "Restaurant AMC Contracts")
        r_inner = r_inner.replace("hotelAmc", "restAmc")
        
        # Remove the add expense head button from restaurant section
        r_inner = re.sub(r"\{can\(\['owner', 'admin', 'accountant'\]\) && \(\n\s*<button onClick=\{\(\) => setNewHeadModalOpen\(true\)\} className=\"text-xs text-navy-600 hover:text-navy-800 font-medium\">\+ Add Expense Head</button>\n\s*\)\}", "", r_inner)

        new_daily = f"""{{activeTab === 'daily' && (
        <>
{h_inner}
          {{(restEntries.length > 0 || restAmc.length > 0) && (
            <div className="mt-10 pt-8 border-t border-slate-200">
{r_inner}
            </div>
          )}}
        </>
      )}}
      """
        content = content.replace(old_daily, new_daily)
        
    # For the purchase tab
    match_purchase = re.search(r"(\{activeTab === 'purchase' && \(\n\s*<>\n\s*<div className=\"flex justify-between items-end mb-3 mt-8\">.*?)(?=\n\s*\)\}\n\n\s*\{purchaseModalOpen && \()", content, re.DOTALL)
    if match_purchase:
        old_purchase = match_purchase.group(1)
        
        h_purchase = old_purchase.replace("Purchase Invoices", "Hotel Purchase Invoices")
        h_purchase = h_purchase.replace("rows={purchaseInvoices}", "rows={hotelPI}")
        
        h_inner = h_purchase.replace("{activeTab === 'purchase' && (\n        <>\n", "")
        h_inner = h_inner.replace("\n        </>\n      )", "")
        
        r_inner = h_inner.replace("Hotel Purchase Invoices", "Restaurant Purchase Invoices")
        r_inner = r_inner.replace("hotelPI", "restPI")
        
        new_purchase = f"""{{activeTab === 'purchase' && (
        <>
{h_inner}
          {{restPI.length > 0 && (
            <div className="mt-10 pt-8 border-t border-slate-200">
{r_inner}
            </div>
          )}}
        </>
      )}}"""
        content = content.replace(old_purchase, new_purchase)

    with open('src/pages/HotelExpenses.jsx', 'w') as f:
        f.write(content)
        
    print("Patched HotelExpenses.jsx successfully")

main()
