import re

def update_modal_fields(file_path, year_state):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 1. Update the fields array in the modal
    old_fields_regex = r"\{\s*type:\s*'select',\s*key:\s*'period',.*?\n\s*\]\s*\}"
    
    new_fields = f"""{{ 
              type: 'select', 
              key: 'reportYear', 
              label: 'Select Year', 
              default: String({year_state}),
              options: [
                {{ value: 'all', label: 'All Available Years' }},
                ...Array.from({{ length: 8 }}, (_, i) => {{ const y = new Date().getFullYear() - 2 + i; return {{ value: String(y), label: String(y) }} }})
              ]
            }},
            {{
              type: 'select',
              key: 'reportMonth',
              label: 'Select Month',
              default: 'all',
              options: [
                {{ value: 'all', label: 'Full Year' }},
                ...Array.from({{ length: 12 }}, (_, i) => {{ return {{ value: String(i + 1), label: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i] }} }})
              ]
            }}"""
    
    # We will use simple replace for the specific block
    # Find the block starting with "{ type: 'select', key: 'period'" and ending with "}"
    old_block_budget = """            { 
              type: 'select', 
              key: 'period', 
              label: 'Select Period', 
              default: String(startYear),
              options: [
                { value: 'all', label: 'All Available Years' },
                ...Array.from({ length: 8 }, (_, i) => { const y = new Date().getFullYear() - 2 + i; return { value: String(y), label: `${y} (Full Year)` } }),
                ...Array.from({ length: 12 }, (_, i) => { return { value: `${startYear}-${i + 1}`, label: `${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i]} ${startYear}` } })
              ]
            }"""
            
    old_block_expense = """            { 
              type: 'select', 
              key: 'period', 
              label: 'Select Period', 
              default: String(selectedYear),
              options: [
                { value: 'all', label: 'All Available Years' },
                ...Array.from({ length: 8 }, (_, i) => { const y = new Date().getFullYear() - 2 + i; return { value: String(y), label: `${y} (Full Year)` } }),
                ...Array.from({ length: 12 }, (_, i) => { return { value: `${selectedYear}-${i + 1}`, label: `${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i]} ${selectedYear}` } })
              ]
            }"""

    if "startYear" in year_state:
        content = content.replace(old_block_budget, new_fields)
    else:
        content = content.replace(old_block_expense, new_fields)

    # 2. Update the generateReport logic to parse reportYear and reportMonth
    old_gen = f"""    const p = selections.period || String({year_state})
    let periodKeys = []
    
    if (p === 'all') {{
      const allYears = Array.from({{ length: 8 }}, (_, i) => new Date().getFullYear() - 2 + i)
      allYears.forEach(y => MONTH_NAMES.forEach((_, i) => periodKeys.push(`${{y}}-${{i + 1}}`)))
    }} else if (p.includes('-')) {{
      periodKeys.push(p)
    }} else {{
      MONTH_NAMES.forEach((_, i) => periodKeys.push(`${{p}}-${{i + 1}}`))
    }}"""

    new_gen = f"""    const pYear = selections.reportYear || String({year_state})
    const pMonth = selections.reportMonth || 'all'
    let periodKeys = []
    
    if (pYear === 'all') {{
      const allYears = Array.from({{ length: 8 }}, (_, i) => new Date().getFullYear() - 2 + i)
      allYears.forEach(y => MONTH_NAMES.forEach((_, i) => periodKeys.push(`${{y}}-${{i + 1}}`)))
    }} else if (pMonth !== 'all') {{
      periodKeys.push(`${{pYear}}-${{pMonth}}`)
    }} else {{
      MONTH_NAMES.forEach((_, i) => periodKeys.push(`${{pYear}}-${{i + 1}}`))
    }}"""

    content = content.replace(old_gen, new_gen)

    # 3. Update subtitle logic
    if year_state == 'startYear':
        # HotelBudget
        content = content.replace("const subtitle = `${activeCompany.name} • ${startYear} • ${selections.currency}`", 
                                  "const subtitle = `${activeCompany.name} • ${pYear === 'all' ? 'All Years' : pYear + (pMonth !== 'all' ? ' ' + MONTH_NAMES[Number(pMonth)-1] : '')} • ${selections.currency}`")
    else:
        # HotelExpenseBudget
        content = content.replace("const subtitle = `${activeCompany.name} • ${p} • ${selections.currency}`",
                                  "const subtitle = `${activeCompany.name} • ${pYear === 'all' ? 'All Years' : pYear + (pMonth !== 'all' ? ' ' + MONTH_NAMES[Number(pMonth)-1] : '')} • ${selections.currency}`")
        content = content.replace("title: p === 'all' ? `All Years Summary` : `${p} Annual Summary`,",
                                  "title: pYear === 'all' ? `All Years Summary` : `${pYear} Annual Summary`,")

    with open(file_path, 'w') as f:
        f.write(content)

update_modal_fields('src/pages/HotelBudget.jsx', 'startYear')
update_modal_fields('src/pages/HotelExpenseBudget.jsx', 'selectedYear')

