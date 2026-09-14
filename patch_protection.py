import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

# Protect Members
member_trash = r'<button onClick=\{\(\) => removeMember\(m\.id\)\} className="text-slate-300 hover:text-red-500"><Trash2 size=\{15\} /></button>'
protected_member_trash = """{(m.profile?.email !== 'crscentral.rm@gmail.com' && m.profile?.email !== user.email && m.invited_email !== 'crscentral.rm@gmail.com') && (
                      <button onClick={() => removeMember(m.id)} className="text-slate-300 hover:text-red-500"><Trash2 size={15} /></button>
                    )}"""

code = re.sub(member_trash, protected_member_trash, code)

# Protect Companies
company_delete_btn = r'<button\s+onClick=\{\(\) => handleCompanyDelete\(c\.id, c\.name\)\}.*?<Trash2 size=\{16\} />\s+</button>'
protected_company_btn = """{c.name !== 'CRS Central' && c.id !== activeCompany.id && (
                        <button
                          onClick={() => handleCompanyDelete(c.id, c.name)}
                          disabled={actionInProgress === c.id}
                          className="flex-shrink-0 text-red-500 hover:text-red-700 bg-red-50 hover:bg-red-100 p-2 rounded-lg transition-colors"
                          title="Delete Company"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}"""

code = re.sub(company_delete_btn, protected_company_btn, code, flags=re.DOTALL)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
