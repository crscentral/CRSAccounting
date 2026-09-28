import re

with open('.github/workflows/nightly-backup.yml', 'r') as f:
    content = f.read()

old_block = """            // Fix SSL requirement for Supabase
            let connectionString = process.env.SUPABASE_DB_URL;
            if (!connectionString.includes('sslmode=require')) {
              connectionString += (connectionString.includes('?') ? '&' : '?') + 'sslmode=require';
            }

            const client = new Client({ 
              connectionString,
              ssl: { rejectUnauthorized: false }
            });"""

new_block = """            // Bulletproof connection string parsing (handles unencoded @ in passwords)
            let rawUrl = process.env.SUPABASE_DB_URL;
            // Remove any query params like ?sslmode=require
            if (rawUrl.includes('?')) rawUrl = rawUrl.split('?')[0];
            
            // Greedy match up to the LAST @ symbol to perfectly extract passwords containing @
            const match = rawUrl.match(/postgres(?:ql)?:\\/\\/([^:]+):(.*)@([^@]+):(\\d+)\\/(.*)/);
            if (!match) {
              console.error('Error: Could not parse database URL correctly.');
              process.exit(1);
            }
            
            let user = match[1];
            let password = match[2];
            // If they URL encoded it (e.g. %40), unencode it. If not, leave it.
            if (password.includes('%')) password = decodeURIComponent(password);
            
            const host = match[3];
            const port = parseInt(match[4], 10);
            const database = match[5];

            const client = new Client({ 
              user,
              password,
              host,
              port,
              database,
              ssl: { rejectUnauthorized: false }
            });"""

content = content.replace(old_block, new_block)

with open('.github/workflows/nightly-backup.yml', 'w') as f:
    f.write(content)
