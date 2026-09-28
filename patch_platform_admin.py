import re

with open('src/pages/Settings.jsx', 'r') as f:
    content = f.read()

guide = """
      <div className="mt-8 bg-slate-50 rounded-xl p-6 border border-slate-200">
        <h3 className="text-lg font-bold text-navy-700 mb-4">Master System Backup Guide</h3>
        <div className="prose prose-sm max-w-none text-slate-600 space-y-4">
          <p><strong>Where is the Master Backup stored?</strong><br/>
          Your master backup runs entirely in the cloud and is securely saved in your <strong>GitHub Repository</strong>. You do not need to link a Google Drive! GitHub acts as your unlimited, free storage vault for 90 days of backups.</p>

          <p><strong>How do I check if the backup ran successfully?</strong><br/>
          1. Go to your code repository on GitHub.com.<br/>
          2. Click the <strong>Actions</strong> tab at the top.<br/>
          3. Click on <strong>Master Nightly Database Backup</strong> on the left.<br/>
          4. You will see a list of every backup. A green checkmark means it succeeded. Click on one to download the <code>.sql</code> backup file to your computer.</p>

          <p><strong>When does it run?</strong><br/>
          It runs automatically every day at 12:00 AM UTC (which is exactly 7:00 AM Thailand Time).</p>

          <p><strong>Is it running right now? (REQUIRED FINAL STEP)</strong><br/>
          For the backup to work tonight, you must give GitHub the password to your database:<br/>
          1. Go to GitHub ➔ <strong>Settings</strong> ➔ <strong>Secrets and variables</strong> ➔ <strong>Actions</strong>.<br/>
          2. Click <strong>New repository secret</strong>.<br/>
          3. Name: <code>SUPABASE_DB_URL</code><br/>
          4. Secret: Paste your Supabase Database Connection String (Found in Supabase ➔ Settings ➔ Database ➔ URI).<br/>
          Once you do this, it will run perfectly forever.</p>

          <p><strong>How do I restore data for just ONE company (e.g. Ramu Mills)?</strong><br/>
          The master GitHub backup saves ALL companies in one massive file. If Ramu Mills makes a mistake and needs data restored, you should instruct them to use the <strong>Backup & Restore</strong> tab in their own Settings page! They can download and upload their own data securely. If they forgot to download a backup, you would have to download the massive GitHub <code>.sql</code> file, search for their specific <code>company_id</code>, and manually run that SQL code in Supabase to restore their data.</p>
        </div>
      </div>
"""

content = content.replace(
    'return <div>Platform Admin settings...</div>',
    'return <div><div>Platform Admin settings...</div>' + guide + '</div>'
)

# Wait, the Platform Admin block might just be `return <div>Platform Admin settings...</div>`
# Let's check how Settings.jsx is structured.
