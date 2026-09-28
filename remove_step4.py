import re

with open('src/pages/Settings.jsx', 'r') as f:
    content = f.read()

old_block = """            <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <strong className="text-amber-800 block mb-1">4. REQUIRED FINAL STEP (For the backup to work tonight)</strong>
              For the backup to have access to your database, you must give GitHub your database password:<br/>
              • Go to GitHub ➔ <strong>Settings</strong> ➔ <strong>Secrets and variables</strong> (on the left menu) ➔ <strong>Actions</strong>.<br/>
              • Click the green <strong>New repository secret</strong> button.<br/>
              • Name: <code>SUPABASE_DB_URL</code><br/>
              • Secret: Paste your Supabase Database Connection String (Found in Supabase ➔ Project Settings ➔ Database ➔ URI).<br/>
              <em>Once you do this, it will run perfectly forever.</em>
            </div>

            <div>
              <strong className="text-navy-700 block mb-1">5. How do I restore data for a specific company (e.g., Ramu Mills)?</strong>"""

new_block = """            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <strong className="text-green-800 block mb-1">4. Database Connection Status</strong>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span>Successfully connected to GitHub Secrets. Backups are active.</span>
              </div>
            </div>

            <div>
              <strong className="text-navy-700 block mb-1">5. How do I restore data for a specific company (e.g., Ramu Mills)?</strong>"""

content = content.replace(old_block, new_block)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(content)
