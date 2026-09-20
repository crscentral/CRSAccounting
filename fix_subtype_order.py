import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

replacement = """                  const subtypes = [...new Set(ancillaryAccounts.map(a => a.subtype))].sort((a, b) => {
                    if (a === 'Other Revenue') return 1;
                    if (b === 'Other Revenue') return -1;
                    const order = { 'Room Revenue': 1, 'Front Office': 1, 'F&B Service': 2 };
                    const oa = order[a] || 99;
                    const ob = order[b] || 99;
                    if (oa !== ob) return oa - ob;
                    return a.localeCompare(b);
                  })"""

content = content.replace("                  const subtypes = [...new Set(ancillaryAccounts.map(a => a.subtype))]", replacement)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
