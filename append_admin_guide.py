import re

with open('src/pages/Settings.jsx', 'r') as f:
    content = f.read()

# We need to find the end of the admin tab rendering.
# It currently has two sections: Pending Company Approvals and Company Products.
# We'll replace the closing div of the Company Products section with the closing div + our new guide.

guide = """
      {tab === 'admin' && isPlatformAdmin && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 w-full mt-6 mb-8">
          <h3 className="font-semibold text-slate-800 text-lg mb-4">Master System Backup Guide</h3>
          <div className="text-sm text-slate-600 space-y-4">
            <div>
              <strong className="text-navy-700 block mb-1">1. Where is the Master Backup stored? (Google Drive?)</strong>
              Your master backup runs entirely in the cloud and is securely saved directly in your <strong>GitHub Repository</strong>. You do NOT need to link a Google Drive! GitHub acts as your unlimited, free storage vault for 90 days of backups.
            </div>

            <div>
              <strong className="text-navy-700 block mb-1">2. How do I check if the backup ran successfully?</strong>
              • Go to your code repository on GitHub.com.<br/>
              • Click the <strong>Actions</strong> tab at the top.<br/>
              • Click on <strong>Master Nightly Database Backup</strong> on the left.<br/>
              • You will see a list of every backup. A green checkmark means it succeeded. Click on one to download the <code>.sql</code> backup file to your computer.
            </div>

            <div>
              <strong className="text-navy-700 block mb-1">3. When does it run? Is it live?</strong>
              It is live right now! It will run automatically every day at 12:00 AM UTC (which is exactly <strong>7:00 AM Thailand Time</strong>).
            </div>

            <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <strong className="text-amber-800 block mb-1">4. REQUIRED FINAL STEP (For the backup to work tonight)</strong>
              For the backup to have access to your database, you must give GitHub your database password:<br/>
              • Go to GitHub ➔ <strong>Settings</strong> ➔ <strong>Secrets and variables</strong> (on the left menu) ➔ <strong>Actions</strong>.<br/>
              • Click the green <strong>New repository secret</strong> button.<br/>
              • Name: <code>SUPABASE_DB_URL</code><br/>
              • Secret: Paste your Supabase Database Connection String (Found in Supabase ➔ Project Settings ➔ Database ➔ URI).<br/>
              <em>Once you do this, it will run perfectly forever.</em>
            </div>

            <div>
              <strong className="text-navy-700 block mb-1">5. How do I restore data for a specific company (e.g., Ramu Mills)?</strong>
              The master GitHub backup saves ALL 100 companies in one massive file. If Ramu Mills makes a mistake and needs data restored:<br/>
              • <strong>Best Way:</strong> Instruct them to use the <strong>Backup & Restore</strong> tab in their own Settings page! They can download and upload their own data securely themselves without affecting anyone else.<br/>
              • <strong>Emergency Way:</strong> If they forgot to download a backup, you would have to download the massive GitHub <code>.sql</code> file to your laptop, open it in a text editor, find the specific lines of code containing their <code>company_id</code>, and manually run that code in the Supabase SQL Editor.
            </div>
          </div>
        </div>
      )}
"""

# Insert it right before the closing `</div>` of the main container, or after the Company Products block.
content = content.replace(
    '        </div>\n      )}\n    </div>',
    '        </div>\n      )}\n' + guide + '\n    </div>'
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(content)
