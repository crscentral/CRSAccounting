with open('.github/workflows/nightly-backup.yml', 'r') as f:
    content = f.read()

old_name = """const comp_name = comp.name.replace(/[^a-zA-Z0-9 -_]/g, '').trim().replace(/ /g, '_');"""
new_name = """const comp_name = (comp.name || 'Unnamed_Company_' + comp_id).replace(/[^a-zA-Z0-9 -_]/g, '').trim().replace(/ /g, '_');"""

content = content.replace(old_name, new_name)

if "  workflow_dispatch:" in content and "  push:" not in content:
    content = content.replace("  workflow_dispatch:", "  workflow_dispatch:\n  push:")

with open('.github/workflows/nightly-backup.yml', 'w') as f:
    f.write(content)
