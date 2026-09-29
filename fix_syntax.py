import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# Fix the Daily tab
old_str = """      />
        </>
      )}

      
          {(restEntries.length > 0 || restAmc.length > 0) && ("""
          
new_str = """      />
          {(restEntries.length > 0 || restAmc.length > 0) && ("""

content = content.replace(old_str, new_str)

# Also fix the closing of the daily tab
old_str2 = """        rows={restAmc}
        emptyMessage="No AMC contracts yet."
      />
            </div>
          )}
        </>
      )}"""
      
new_str2 = """        rows={restAmc}
        emptyMessage="No AMC contracts yet."
      />
            </div>
          )}
        </>
      )}"""

# Let's check where the restAmc ends
match = re.search(r"(rows=\{restAmc\}\n\s*emptyMessage=\"No AMC contracts yet\.\"\n\s*\/>\n\s*<\/div>\n\s*\)\})", content)
if match:
    content = content[:match.end()] + "\n        </>\n      )\n" + content[match.end():]

# Let's do the same for purchase tab
old_p = """            emptyMessage="No purchase invoices yet."
          />
        </>
      )}
          {restPI.length > 0 && ("""

new_p = """            emptyMessage="No purchase invoices yet."
          />
          {restPI.length > 0 && ("""
          
content = content.replace(old_p, new_p)

match_p = re.search(r"(rows=\{restPI\}\n\s*emptyMessage=\"No purchase invoices yet\.\"\n\s*\/>\n\s*<\/div>\n\s*\)\})", content)
if match_p:
    content = content[:match_p.end()] + "\n        </>\n      )\n" + content[match_p.end():]


with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
