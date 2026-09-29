import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# Find the start of the calculations (after activeCompany check)
target = """  if (!activeCompany) return null

  const start = new Date(cp.range.from)"""

replacement = """  if (!activeCompany) return null
  
  try {
    const start = new Date(cp.range.from)"""

content = content.replace(target, replacement)

# Find the end of the return statement
target_end = """        </Modal>
      )}
    </div>
  )
}"""

replacement_end = """        </Modal>
      )}
    </div>
  )
  } catch(err) {
    return <div style={{padding: 50, color: 'red', fontSize: 20}}><h1>Runtime Error</h1><pre>{err.stack}</pre></div>;
  }
}"""

content = content.replace(target_end, replacement_end)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
