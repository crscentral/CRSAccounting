import re

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the line: let combined = entries || []
    # Replace it with the filter logic
    
    old_line = "let combined = entries || []"
    
    new_logic = """const ignoredSources = ['restaurant_revenue', 'hotel_room_stats', 'hotel_revenue_entry', 'hotel_expense_entry', 'hotel_amc', 'hotel_guest_invoice', 'owner_contribution', 'owner_dividend', 'loan_taken', 'loan_principal']
    const filteredEntries = (entries || []).filter(e => {
      if (['hotel', 'restaurant'].includes(activeProduct)) {
        return !ignoredSources.includes(e.source_type)
      }
      return true
    })
    let combined = [...filteredEntries]"""
    
    if old_line in content:
        content = content.replace(old_line, new_logic)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Patched {filepath}")
    else:
        # In Ledger.jsx, it might be: let combined = data || []
        old_line_2 = "let combined = data || []"
        if old_line_2 in content:
            new_logic_2 = new_logic.replace("entries || []", "data || []")
            content = content.replace(old_line_2, new_logic_2)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Patched {filepath} (data || [])")
        else:
            print(f"Could not find old_line in {filepath}")

patch_file('src/pages/Reports.jsx')
patch_file('src/pages/Ledger.jsx')
patch_file('src/pages/Comparison.jsx')
