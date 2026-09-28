with open('.github/workflows/nightly-backup.yml', 'r') as f:
    content = f.read()

old_step = """      - name: Generate Individual Company Backups via API
        env:
          SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: |
          npm init -y
          npm install @supabase/supabase-js
          
          node -e "
          const { createClient } = require('@supabase/supabase-js');
          const fs = require('fs');
          
          async function run() {
            if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
              console.error('Error: Missing secrets! Please ensure VITE_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are added to GitHub Secrets.');
              process.exit(1);
            }
            
            const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY, {
              auth: { persistSession: false }
            });
            
            try {
              const { data: companies, error: compErr } = await supabase.from('companies').select('id, name');
              if (compErr) throw compErr;
              if (!companies) throw new Error('No companies found');
              
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
                const comp_name = (comp.name || 'Unnamed_Company_' + comp_id).replace(/[^a-zA-Z0-9 -_]/g, '').trim().replace(/ /g, '_');
                const backup_data = {};
                
                for (const table of tables) {
                  const { data: tableData, error: tblErr } = await supabase
                    .from(table)
                    .select('*')
                    .eq('company_id', comp_id);
                  if (tblErr) {
                    console.log(\`Skipping \${table} for \${comp_name}: \${tblErr.message}\`);
                    continue;
                  }
                  backup_data[table] = tableData || [];
                }
                
                fs.writeFileSync(\`company_backups/\${comp_name}_backup.json\`, JSON.stringify(backup_data, null, 2));
              }
              
              console.log('Successfully generated backups for ' + companies.length + ' companies.');
            } catch (err) {
              console.error('API Error:', err);
              process.exit(1);
            }
          }
          
          run();
          \""""

new_step = """      - name: Generate Individual Company Backups via API
        env:
          SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: |
          node -e "
          const fs = require('fs');
          
          async function fetchSupabase(path) {
            const url = (process.env.SUPABASE_URL || '').trim();
            const key = (process.env.SUPABASE_SERVICE_KEY || '').trim();
            
            if (!url || !key) {
              console.error('Missing secrets! Ensure VITE_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set.');
              process.exit(1);
            }

            const response = await fetch(url + '/rest/v1/' + path, {
              headers: {
                'apikey': key,
                'Authorization': 'Bearer ' + key,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
              }
            });
            
            if (!response.ok) {
              const text = await response.text();
              throw new Error('API Error ' + response.status + ': ' + text);
            }
            
            return await response.json();
          }
          
          async function run() {
            try {
              console.log('Fetching companies...');
              const companies = await fetchSupabase('companies?select=id,name');
              
              if (!companies || companies.length === 0) {
                console.log('No companies found.');
                process.exit(0);
              }
              
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
                const comp_name = (comp.name || 'Unnamed_Company_' + comp_id).replace(/[^a-zA-Z0-9 -_]/g, '').trim().replace(/ /g, '_');
                const backup_data = {};
                
                for (const table of tables) {
                  try {
                    const tableData = await fetchSupabase(table + '?company_id=eq.' + comp_id);
                    backup_data[table] = tableData || [];
                  } catch (e) {
                    console.log('Skipping ' + table + ' for ' + comp_name + ': ' + e.message);
                  }
                }
                
                fs.writeFileSync('company_backups/' + comp_name + '_backup.json', JSON.stringify(backup_data, null, 2));
              }
              
              console.log('Successfully generated backups for ' + companies.length + ' companies.');
            } catch (err) {
              console.error(err);
              process.exit(1);
            }
          }
          
          run();
          "
"""

content = content.replace(old_step, new_step)

if "  workflow_dispatch:" in content and "  push:" not in content:
    content = content.replace("  workflow_dispatch:", "  workflow_dispatch:\n  push:")

with open('.github/workflows/nightly-backup.yml', 'w') as f:
    f.write(content)
