with open('.github/workflows/nightly-backup.yml', 'r') as f:
    content = f.read()

# Replace the entire Python step with a Node.js step
old_step = """      - name: Generate Individual Company Backups
        env:
          SUPABASE_DB_URL: ${{ secrets.SUPABASE_DB_URL }}
        shell: python
        run: |
          import psycopg2
          import psycopg2.extras
          import json
          import os
          import sys
          import urllib.parse
          from datetime import date, datetime

          db_url = os.environ.get('SUPABASE_DB_URL')
          if not db_url:
              print("Error: SUPABASE_DB_URL secret is missing! Please add it to GitHub Secrets.")
              sys.exit(1)

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
          )
          cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

          cur.execute("SELECT id, name FROM companies")
          companies = cur.fetchall()

          tables = [
              'accounts', 'contacts', 'hotel_settings', 'hotel_expense_budget',
              'hotel_room_revenue_budget', 'forecast_entries', 'sales_invoices',
              'purchase_invoices', 'payment_receipts', 'hotel_expense_entries',
              'hotel_amc_contracts', 'hotel_room_stats', 'hotel_guest_invoices',
              'restaurant_daily_revenue', 'ledger_entries'
          ]

          os.makedirs("company_backups", exist_ok=True)

          for comp in companies:
              comp_id = comp['id']
              comp_name = "".join(x for x in comp['name'] if x.isalnum() or x in " _-").strip().replace(' ', '_')
              backup_data = {}
              
              for table in tables:
                  cur.execute(f"SELECT * FROM {table} WHERE company_id = %s", (comp_id,))
                  backup_data[table] = cur.fetchall()
                  
              filename = f"company_backups/{comp_name}_backup.json"
              with open(filename, "w") as f:
                  json.dump(backup_data, f, default=json_serial)

          print(f"Successfully generated backups for {len(companies)} companies.")"""

new_step = """      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Generate Individual Company Backups
        env:
          SUPABASE_DB_URL: ${{ secrets.SUPABASE_DB_URL }}
        run: |
          npm init -y
          npm install pg
          
          node -e "
          const { Client } = require('pg');
          const fs = require('fs');
          
          async function run() {
            if (!process.env.SUPABASE_DB_URL) {
              console.error('Error: SUPABASE_DB_URL missing');
              process.exit(1);
            }
            
            // Fix SSL requirement for Supabase
            let connectionString = process.env.SUPABASE_DB_URL;
            if (!connectionString.includes('sslmode=require')) {
              connectionString += (connectionString.includes('?') ? '&' : '?') + 'sslmode=require';
            }

            const client = new Client({ connectionString });
            
            try {
              await client.connect();
              
              const res = await client.query('SELECT id, name FROM companies');
              const companies = res.rows;
              
              const tables = [
                'accounts', 'contacts', 'hotel_settings', 'hotel_expense_budget',
                'hotel_room_revenue_budget', 'forecast_entries', 'sales_invoices',
                'purchase_invoices', 'payment_receipts', 'hotel_expense_entries',
                'hotel_amc_contracts', 'hotel_room_stats', 'hotel_guest_invoices',
                'restaurant_daily_revenue', 'ledger_entries'
              ];
              
              if (!fs.existsSync('company_backups')) {
                fs.mkdirSync('company_backups');
              }
              
              for (const comp of companies) {
                const comp_id = comp.id;
                const comp_name = comp.name.replace(/[^a-zA-Z0-9 -_]/g, '').trim().replace(/ /g, '_');
                const backup_data = {};
                
                for (const table of tables) {
                  const tableRes = await client.query(\`SELECT * FROM \${table} WHERE company_id = $1\`, [comp_id]);
                  backup_data[table] = tableRes.rows;
                }
                
                fs.writeFileSync(\`company_backups/\${comp_name}_backup.json\`, JSON.stringify(backup_data, null, 2));
              }
              
              console.log('Successfully generated backups for ' + companies.length + ' companies.');
              await client.end();
            } catch (err) {
              console.error('Database Error:', err);
              process.exit(1);
            }
          }
          
          run();
          "
"""

content = content.replace(old_step, new_step)

# Add push trigger back
if "  workflow_dispatch:" in content and "  push:" not in content:
    content = content.replace("  workflow_dispatch:", "  workflow_dispatch:\n  push:")

with open('.github/workflows/nightly-backup.yml', 'w') as f:
    f.write(content)
