import re

with open('src/pages/TallyMode/TallyGateway.jsx', 'r') as f:
    content = f.read()

# Add state and effect for last entry date
imports = """import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../lib/AuthContext'
import { useCurrencyAndPeriod } from '../../lib/useCurrencyAndPeriod'
import { supabase } from '../../lib/supabaseClient'
import { useState, useEffect } from 'react'"""
content = content.replace("import { useState, useEffect } from 'react'", "")
content = content.replace(
    "import { useNavigate } from 'react-router-dom'\nimport { useAuth } from '../../lib/AuthContext'\nimport { useCurrencyAndPeriod } from '../../lib/useCurrencyAndPeriod'",
    imports
)

# Add state inside component
old_start = """export default function TallyGateway() {
  const navigate = useNavigate()
  const { activeCompany } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [selectedIndex, setSelectedIndex] = useState(0)"""

new_start = """export default function TallyGateway() {
  const navigate = useNavigate()
  const { activeCompany, activeProduct } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [lastEntryDate, setLastEntryDate] = useState(null)
  
  useEffect(() => {
    if (activeCompany) {
      supabase.from('ledger_entries')
        .select('entry_date')
        .eq('company_id', activeCompany.id)
        .eq('product', activeProduct)
        .order('entry_date', { ascending: false })
        .limit(1)
        .then(({ data }) => {
          if (data && data.length > 0) {
            setLastEntryDate(data[0].entry_date)
          } else {
            setLastEntryDate(null)
          }
        })
    }
  }, [activeCompany, activeProduct])"""
content = content.replace(old_start, new_start)

# Replace hardcoded text
old_text = """<div className="font-normal text-[12px] italic">No Vouchers Entered</div>"""
new_text = """<div className="font-normal text-[12px] font-bold text-slate-800">{lastEntryDate || <span className="italic font-normal">No Vouchers Entered</span>}</div>"""
content = content.replace(old_text, new_text)


with open('src/pages/TallyMode/TallyGateway.jsx', 'w') as f:
    f.write(content)
