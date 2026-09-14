import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

# Add removeMember function after inviteMember
remove_logic = """  async function removeMember(memberId) {
    if (!confirm('Are you sure you want to remove this user from the company?')) return
    const { error } = await supabase.from('company_members').delete().eq('id', memberId)
    if (error) { alert(error.message); return }
    loadMembers()
  }"""

code = code.replace(
    'async function handleCompanyDelete',
    remove_logic + '\n\n  async function handleCompanyDelete'
)

# Update the Trash button
code = code.replace(
    '<button className="text-slate-300 hover:text-red-500"><Trash2 size={15} /></button>',
    '<button onClick={() => removeMember(m.id)} className="text-slate-300 hover:text-red-500"><Trash2 size={15} /></button>'
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
