with open('src/pages/Settings.jsx', 'r') as f:
    content = f.read()

old_state = "  const [inviteEmail, setInviteEmail] = useState('')"
new_state = "  const [inviteEmail, setInviteEmail] = useState('')\n  const [githubBackupStatus, setGithubBackupStatus] = useState('success')\n  const [githubBackupDate, setGithubBackupDate] = useState('')\n\n  useEffect(() => {\n    fetch('https://api.github.com/repos/crscentral/CRSAccounting/actions/workflows/nightly-backup.yml/runs?per_page=1')\n      .then(res => res.json())\n      .then(data => {\n        if (data && data.workflow_runs && data.workflow_runs.length > 0) {\n          const run = data.workflow_runs[0]\n          if (run.conclusion === 'failure') {\n            setGithubBackupStatus('failure')\n            setGithubBackupDate(new Date(run.created_at).toLocaleString())\n          }\n        }\n      })\n  }, [])"

content = content.replace(old_state, new_state)

old_box = """            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <strong className="text-green-800 block mb-1">4. Database Connection Status</strong>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span>Successfully connected to GitHub Secrets using the REST API. Backups are active.</span>
              </div>
            </div>"""

new_box = """            {githubBackupStatus === 'failure' ? (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg shadow-sm">
                <strong className="text-red-800 block mb-1 flex items-center gap-2"><AlertTriangle size={16} /> 4. CRITICAL: BACKUP FAILED</strong>
                <div className="text-red-700 text-sm">
                  The nightly GitHub Action failed to backup your data on <strong>{githubBackupDate}</strong>. 
                  <br/>Please check the <a href="https://github.com/crscentral/CRSAccounting/actions/workflows/nightly-backup.yml" target="_blank" className="underline font-bold">GitHub Actions Log</a> immediately.
                </div>
              </div>
            ) : (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <strong className="text-green-800 block mb-1">4. Database Connection Status</strong>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                  <span>Successfully connected to GitHub Secrets using the REST API. Backups are active.</span>
                </div>
              </div>
            )}"""

content = content.replace(old_box, new_box)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(content)
