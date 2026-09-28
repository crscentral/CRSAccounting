with open('.github/workflows/nightly-backup.yml', 'r') as f:
    content = f.read()

if "  workflow_dispatch:" in content and "  push:" not in content:
    content = content.replace("  workflow_dispatch:", "  workflow_dispatch:\n  push:")

with open('.github/workflows/nightly-backup.yml', 'w') as f:
    f.write(content)
