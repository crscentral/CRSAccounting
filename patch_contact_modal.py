import re

with open('src/components/ContactFormModal.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "function ContactFormModal({ type, companyId, contact, onClose, onSaved }) {",
    "function ContactFormModal({ type, companyId, product, contact, onClose, onSaved }) {"
)

content = content.replace(
    "await supabase.from('contacts').insert({ ...form, company_id: companyId })",
    "await supabase.from('contacts').insert({ ...form, company_id: companyId, product })"
)

with open('src/components/ContactFormModal.jsx', 'w') as f:
    f.write(content)
