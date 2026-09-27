import re

with open('src/pages/Contacts.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "companyId={activeCompany.id}",
    "companyId={activeCompany.id}\n          product={activeProduct}"
)

with open('src/pages/Contacts.jsx', 'w') as f:
    f.write(content)
