import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

# Put it back
code = code.replace(
    ".select('*')",
    ".select('*, members:company_members(role, user_id, profile:user_profiles(email, full_name))')"
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
