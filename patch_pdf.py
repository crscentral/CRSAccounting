import re

with open('src/pages/Reports.jsx', 'r') as f:
    code = f.read()

new_income_statement = """    } else if (reportKey === 'income_statement') {
      sections = [
        {
          heading: 'Income Statement',
          headColor: [5, 150, 105], // emerald-600
          columns: ['REVENUE', '% of Total', 'Amount'],
          rows: [
            ...by('Revenue').map(a => {
              const v = -(bal[a.id] || 0)
              const pct = rev ? ((v / rev) * 100).toFixed(1) + '%' : '0.0%'
              return [a.name, pct, fmt(v)]
            }),
            ['Total Revenue', '100.0%', fmt(rev)]
          ]
        },
        {
          heading: '',
          headColor: [225, 29, 72], // rose-600
          columns: ['OPERATING EXPENSES', '% of Total', 'Amount'],
          rows: [
            ...operatingAccs.map(a => {
              const v = bal[a.id] || 0
              const pct = opExp ? ((v / opExp) * 100).toFixed(1) + '%' : '0.0%'
              return [a.name, pct, fmt(v)]
            }),
            ['Total Operating Expenses', '100.0%', fmt(opExp)]
          ]
        },
        {
          heading: '',
          headColor: [27, 58, 107], // navy
          columns: ['Profitability & Other', '% of Revenue', 'Amount'],
          rows: [
            [gopVal >= 0 ? 'GOP (Gross Operating Profit)' : 'GOL (Gross Operating Loss)', rev ? ((gopVal / rev) * 100).toFixed(1) + '%' : '0.0%', fmt(gopVal)],
            ...(otherBelowLineAccs.length > 0 ? [...otherBelowLineAccs.map(a => [a.name, '', fmt(bal[a.id] || 0)]), ['Management Fees, Taxes, Rent & Licenses', '', fmt(otherBL)]] : []),
            ['EBITDA', rev ? ((ebitdaVal / rev) * 100).toFixed(1) + '%' : '0.0%', fmt(ebitdaVal)],
            ...(daInterestAccs.length > 0 ? [...daInterestAccs.map(a => [a.name, '', fmt(bal[a.id] || 0)]), ['Depreciation & Interest', '', fmt(daInt)]] : []),
            ['Net Income', rev ? (((rev - exp) / rev) * 100).toFixed(1) + '%' : '0.0%', fmt(rev - exp)]
          ]
        }
      ]
    }"""

code = re.sub(
    r"    \} else if \(reportKey === 'income_statement'\) \{\n      sections = \[\{\n        heading: 'Income Statement',\n        columns: \['Item', 'Amount'\],\n        rows: \[\n          \.\.\.by\('Revenue'\)\.map\(a => \[a\.name, fmt\(-\(bal\[a\.id\] \|\| 0\)\)\]\),\n          \['Total Revenue', fmt\(rev\)\],\n          \.\.\.operatingAccs\.map\(a => \[a\.name, fmt\(bal\[a\.id\] \|\| 0\)\]\),\n          \['Total Operating Expenses', fmt\(opExp\)\],\n          \[gopVal >= 0 \? 'GOP \(Gross Operating Profit\)' : 'GOL \(Gross Operating Loss\)', fmt\(gopVal\)\],\n          \.\.\.\(otherBelowLineAccs\.length > 0 \? \[\.\.\.otherBelowLineAccs\.map\(a => \[a\.name, fmt\(bal\[a\.id\] \|\| 0\)\]\), \['Management Fees, Taxes, Rent & Licenses', fmt\(otherBL\)\]\] : \[\]\),\n          \['EBITDA', fmt\(ebitdaVal\)\],\n          \.\.\.\(daInterestAccs\.length > 0 \? \[\.\.\.daInterestAccs\.map\(a => \[a\.name, fmt\(bal\[a\.id\] \|\| 0\)\]\), \['Depreciation & Interest', fmt\(daInt\)\]\] : \[\]\),\n          \['Net Income', fmt\(rev - exp\)\],\n        \],\n      \}\]\n    \}",
    new_income_statement,
    code
)

with open('src/pages/Reports.jsx', 'w') as f:
    f.write(code)
