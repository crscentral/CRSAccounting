with open('.github/workflows/nightly-backup.yml', 'r') as f:
    content = f.read()

old_python = """          conn = psycopg2.connect(db_url)"""
new_python = """          import urllib.parse
          result = urllib.parse.urlparse(db_url)
          
          # Manually extract and decode the password to fix the %40 issue
          username = result.username
          password = urllib.parse.unquote(result.password) if result.password else None
          database = result.path[1:]
          hostname = result.hostname
          port = result.port

          conn = psycopg2.connect(
              database=database,
              user=username,
              password=password,
              host=hostname,
              port=port
          )"""

content = content.replace(old_python, new_python)

# also add push back so I can trigger it
if "  workflow_dispatch:" in content and "  push:" not in content:
    content = content.replace("  workflow_dispatch:", "  workflow_dispatch:\n  push:")

with open('.github/workflows/nightly-backup.yml', 'w') as f:
    f.write(content)
