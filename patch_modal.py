with open('src/components/AccountFormModal.jsx', 'r') as f:
    content = f.read()

func = """
  async function handleNameBlur() {
    if (!form.name.trim() || account) return
    const { data } = await supabase.from('accounts').select('code, type, subtype').eq('company_id', companyId).ilike('name', form.name.trim()).limit(1).maybeSingle()
    if (data) {
      setForm(f => ({ ...f, code: data.code, type: data.type, subtype: data.subtype || f.subtype }))
    }
  }

  async function handleSubmit(e) {"""

content = content.replace("  async function handleSubmit(e) {", func)

input_name = """<input required value={form.name} onChange={e => update('name', e.target.value)}"""
input_name_new = """<input required value={form.name} onChange={e => update('name', e.target.value)} onBlur={handleNameBlur}"""

content = content.replace(input_name, input_name_new)

with open('src/components/AccountFormModal.jsx', 'w') as f:
    f.write(content)
