import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

old_kpi_calc = """    let frontOffice = roomRev
    let fbService = 0
    let otherRev = 0

    for (let m = 1; m <= 12; m++) {
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        const budgetUsd = ancillaryBudgets[k] ? Number(ancillaryBudgets[k].amount_usd) : 0
        
        if (a.subtype === 'Front Office') frontOffice += budgetUsd
        else if (a.subtype === 'F&B Service') fbService += budgetUsd
        else otherRev += budgetUsd
      }
    }
    
    return { frontOffice, fbService, otherRev }"""

new_kpi_calc = """    let frontOffice = roomRev
    let fbService = 0
    let otherRev = 0

    for (let m = 1; m <= 12; m++) {
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        const budgetUsd = ancillaryBudgets[k] ? Number(ancillaryBudgets[k].amount_usd) : 0
        
        if (activeProduct === 'restaurant') {
          if ((a.subtype || '').toLowerCase().includes('revenue') || (a.name || '').toLowerCase().includes('food')) {
            frontOffice += budgetUsd
          } else if ((a.subtype || '').toLowerCase().includes('service') || (a.name || '').toLowerCase().includes('beverage')) {
            fbService += budgetUsd
          } else {
            otherRev += budgetUsd
          }
        } else {
          if (a.subtype === 'Front Office') frontOffice += budgetUsd
          else if (a.subtype === 'F&B Service') fbService += budgetUsd
          else otherRev += budgetUsd
        }
      }
    }
    
    return { frontOffice, fbService, otherRev }"""

content = content.replace(old_kpi_calc, new_kpi_calc)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
