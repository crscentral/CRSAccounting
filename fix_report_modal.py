import re

def patch():
    with open('src/components/ReportOptionsModal.jsx', 'r') as f:
        content = f.read()

    # Find the useState lines
    old_states = """  const initial = {}
  fields.forEach(f => { initial[f.key] = f.default })
  const [values, setValues] = useState(initial)
  const [customFrom, setCustomFrom] = useState('')
  const [customTo, setCustomTo] = useState('')"""
    
    new_states = """  const initial = {}
  let defFrom = ''
  let defTo = ''
  fields.forEach(f => { 
    initial[f.key] = f.default 
    if (f.type === 'period') {
      defFrom = f.defaultFrom || ''
      defTo = f.defaultTo || ''
    }
  })
  const [values, setValues] = useState(initial)
  const [customFrom, setCustomFrom] = useState(defFrom)
  const [customTo, setCustomTo] = useState(defTo)"""

    content = content.replace(old_states, new_states)
    
    with open('src/components/ReportOptionsModal.jsx', 'w') as f:
        f.write(content)
        print("Patched ReportOptionsModal.jsx")

patch()
