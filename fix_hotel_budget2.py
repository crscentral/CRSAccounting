import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

old_fmt = r"function fmt\(usd\) \{ return formatMoney\(convertFromUsd\(usd, displayCurrency, \{ \[displayCurrency\]: rate \}\), displayCurrency\) \}"
new_fmt = """function fmt(usd) { return formatMoney(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }), displayCurrency) }
  function fmtRoundedAbs(usd) { return formatMoney(Math.abs(Math.round(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }))), displayCurrency).replace('.00', '') }
  function fmtRounded(usd) { return formatMoney(Math.round(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate })), displayCurrency).replace('.00', '') }"""
code = re.sub(old_fmt, new_fmt, code)

old_pace = r"value=\{fmt\(mtdPaceVariance\)\}"
new_pace = r"value={fmtRoundedAbs(mtdPaceVariance)}"
code = re.sub(old_pace, new_pace, code)

old_month_budget = r"value=\{fmt\(currentMonthBudget\)\}"
new_month_budget = r"value={fmtRounded(currentMonthBudget)}"
code = re.sub(old_month_budget, new_month_budget, code)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
