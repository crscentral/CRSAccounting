import re

with open('src/pages/Settings.jsx', 'r') as f:
    content = f.read()

old_guide = """            <div>
              <strong className="text-navy-700 block mb-1">5. How do I restore data for a specific company (e.g., Ramu Mills)?</strong>
              The master GitHub backup saves ALL 100 companies in one massive file. If Ramu Mills makes a mistake and needs data restored:<br/>
              • <strong>Best Way:</strong> Instruct them to use the <strong>Backup & Restore</strong> tab in their own Settings page! They can download and upload their own data securely themselves without affecting anyone else.<br/>
              • <strong>Emergency Way:</strong> If they forgot to download a backup, you would have to download the massive GitHub <code>.sql</code> file to your laptop, open it in a text editor, find the specific lines of code containing their <code>company_id</code>, and manually run that code in the Supabase SQL Editor.
            </div>"""

new_guide = """            <div>
              <strong className="text-navy-700 block mb-1">5. How do I restore data for a specific company (e.g., Ramu Mills)?</strong>
              I have custom-built the master backup system to automatically slice the database into individual, ready-to-use files for each company! If Ramu Mills crashes and asks for help:<br/>
              1. Download last night's <code>all_company_backups.zip</code> file from the GitHub Actions tab.<br/>
              2. Open the zip file on your laptop. Inside, you will see a neatly labeled file named <code>Ramu_Mills_backup.json</code>.<br/>
              3. Here in the web application, use the Company Switcher at the top left to switch into <strong>Ramu Mills</strong>.<br/>
              4. Come right back to this Settings page, click their <strong>Backup & Restore</strong> tab, and simply upload the <code>Ramu_Mills_backup.json</code> file.<br/>
              <em>Boom! Their entire company is instantly restored, and no other company is affected! You never have to touch a line of code.</em>
            </div>"""

content = content.replace(old_guide, new_guide)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(content)
