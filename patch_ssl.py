with open('.github/workflows/nightly-backup.yml', 'r') as f:
    content = f.read()

# Replace the Client initialization
old_client = """            const client = new Client({ connectionString });"""
new_client = """            const client = new Client({ 
              connectionString,
              ssl: { rejectUnauthorized: false }
            });"""

content = content.replace(old_client, new_client)

if "  workflow_dispatch:" in content and "  push:" not in content:
    content = content.replace("  workflow_dispatch:", "  workflow_dispatch:\n  push:")

with open('.github/workflows/nightly-backup.yml', 'w') as f:
    f.write(content)
