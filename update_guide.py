with open('src/pages/Settings.jsx', 'r') as f:
    content = f.read()

# Wait, I previously changed the guide to "Successfully connected to GitHub Secrets".
# But wait, they need to add a NEW secret now!
# So I should change the guide back to telling them to add `SUPABASE_SERVICE_ROLE_KEY`.
old_block = """            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <strong className="text-green-800 block mb-1">4. Database Connection Status</strong>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span>Successfully connected to GitHub Secrets. Backups are active.</span>
              </div>
            </div>"""

new_block = """            <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <strong className="text-amber-800 block mb-1">4. REQUIRED FINAL STEP (For the backup to work tonight)</strong>
              We have completely upgraded the backup system to use the 100% reliable REST API instead of direct connection. You must give GitHub your Service Role Key:<br/>
              • Go to GitHub ➔ <strong>Settings</strong> ➔ <strong>Secrets and variables</strong> ➔ <strong>Actions</strong>.<br/>
              • Click <strong>New repository secret</strong>.<br/>
              • Name: <code>SUPABASE_SERVICE_ROLE_KEY</code><br/>
              • Secret: Paste your Service Role Key (Found in Supabase ➔ Project Settings ➔ API ➔ <code>service_role</code>).<br/>
              <em>You can safely delete the old SUPABASE_DB_URL secret.</em>
            </div>"""

content = content.replace(old_block, new_block)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(content)

with open('public/sw.js', 'r') as f:
    sw = f.read()
sw = sw.replace("crs-accounting-shell-v109", "crs-accounting-shell-v110")
with open('public/sw.js', 'w') as f:
    f.write(sw)
