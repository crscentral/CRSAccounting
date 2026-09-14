import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Update Pie Chart 2 data names
code = code.replace("{ name: 'Collected', value: cp.convert(collected), color: '#10b981' }", "{ name: 'Revenue', value: cp.convert(collected), color: '#10b981' }")
code = code.replace("{ name: 'Made', value: cp.convert(expensesMade), color: '#f97316' }", "{ name: 'Expense', value: cp.convert(expensesMade), color: '#f97316' }")

# Update the legend below Pie Chart 2
# It currently has: <span className="w-3 h-3 rounded-full bg-yellow-500"></span> Collected: {cp.fmt(collected)}
# Actually wait, color for collected in pie was #10b981 which is green! Oh wait, I set it to green `#10b981` in patch_charts4.py!
# But the legend has `bg-yellow-500`? No, let's just replace the legend words.

code = code.replace("Collected: {cp.fmt(collected)}", "Revenue: {cp.fmt(collected)}")
code = code.replace("Made: {cp.fmt(expensesMade)}", "Expense: {cp.fmt(expensesMade)}")

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
