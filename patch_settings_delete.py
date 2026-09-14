import re
with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

delete_fn = """  async function handleCompanyDelete(companyId, companyName) {
    const word = prompt(`WARNING: This will completely delete the company "${companyName}" and ALL of its data. This cannot be undone.\\n\\nType DELETE to confirm:`)
    if (word !== 'DELETE') return
    
    setActionInProgress(companyId)
    const { error } = await supabase.from('companies').delete().eq('id', companyId)
    if (error) {
      alert(error.message)
    } else {
      await Promise.all([loadAllCompaniesProducts(), loadPendingCompanies()])
    }
    setActionInProgress(null)
  }

  async function decideCompany"""

code = code.replace("  async function decideCompany", delete_fn)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
