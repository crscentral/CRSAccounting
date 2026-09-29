import re

with open('src/pages/CapitalTransactions.jsx', 'r') as f:
    content = f.read()

# The junk block is exactly:
junk = """  const currentList = tab === 'equity' ? ownerContributions :
                      tab === 'loans_taken' ? loansTaken :
                      tab === 'dividends' ? dividends :
                      loanPayments

  const byCurrency = {}
  let totalUsd = 0
  currentList.forEach(i => {
    byCurrency[i.currency] = byCurrency[i.currency] || { native: 0, usd: 0, count: 0 }
    byCurrency[i.currency].native += Number(i.amount)
    byCurrency[i.currency].usd += Number(i.amount_usd)
    byCurrency[i.currency].count++
    totalUsd += Number(i.amount_usd)
  })
"""

# Let's count how many times it appears
print(f"Junk block appears {content.count(junk)} times.")

# We ONLY want to keep it in the main component `CapitalTransactions`.
# Wait, let's see where it belongs. It belongs inside `export default function CapitalTransactions`.
# It's probably already there! 
# Let's just remove it from all functions whose name ends with `Modal`.

# We can find each modal function and delete the junk block inside it.
def remove_junk_from_modals(content):
    modals = ['LoanRepaymentFormModal', 'DividendFormModal', 'OwnerEquityFormModal', 'LoanTakenFormModal']
    for modal in modals:
        # We need a robust way. Let's just do a regex that finds the junk block between `function ModalName` and `return (`
        pattern = rf"(function {modal}\([^)]*\) {{.*?){re.escape(junk)}(.*?(?:return \(|<Modal))"
        # Wait, regex might fail if it's too long.
        pass

# Actually, we can just replace the junk block with empty string everywhere AFTER the main export default function!
# Let's split the file at `function LoanRepaymentFormModal`
parts = content.split("function LoanRepaymentFormModal")
if len(parts) == 2:
    main_part = parts[0]
    modals_part = "function LoanRepaymentFormModal" + parts[1]
    
    # Remove all junk from modals_part
    modals_part = modals_part.replace(junk, "")
    
    with open('src/pages/CapitalTransactions.jsx', 'w') as f:
        f.write(main_part + modals_part)
else:
    print("Could not split file!")
