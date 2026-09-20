import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

old_inject = """          if (b > 0 && acc4020) { revMap[acc4020.id] = revMap[acc4020.id] || { code: acc4020.code, name: acc4020.name, amount: 0 }; revMap[acc4020.id].amount += b }
          if (o > 0 && acc4021) { revMap[acc4021.id] = revMap[acc4021.id] || { code: acc4021.code, name: acc4021.name, amount: 0 }; revMap[acc4021.id].amount += o }
        } else if (activeProduct === 'restaurant') {
          const acc4016 = accs.find(a => a.code === '4016'); const acc4010 = accs.find(a => a.code === '4010');
          const acc4011 = accs.find(a => a.code === '4011'); const acc4019 = accs.find(a => a.code === '4019');
          if (f > 0) { const acc = r.meal_period === 'Breakfast' ? acc4016 : acc4010; if (acc) { revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; revMap[acc.id].amount += f } }
          if (b > 0 && acc4011) { revMap[acc4011.id] = revMap[acc4011.id] || { code: acc4011.code, name: acc4011.name, amount: 0 }; revMap[acc4011.id].amount += b }
          if (o > 0 && acc4019) { revMap[acc4019.id] = revMap[acc4019.id] || { code: acc4019.code, name: acc4019.name, amount: 0 }; revMap[acc4019.id].amount += o }
        }"""

new_inject = """          if (b > 0 && acc4020) { revMap[acc4020.id] = revMap[acc4020.id] || { code: acc4020.code, name: acc4020.name, amount: 0 }; revMap[acc4020.id].amount += b }
          if (o > 0 && acc4021) { revMap[acc4021.id] = revMap[acc4021.id] || { code: acc4021.code, name: acc4021.name, amount: 0 }; revMap[acc4021.id].amount += o }
        }
        // Do not inject for restaurant because Table Revenue is already in ledger_entries."""

content = content.replace(old_inject, new_inject)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)

