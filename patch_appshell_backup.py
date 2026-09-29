with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

old_state = "  const { activeCompany, user, activeProduct, setActiveProduct } = useAuth()"
new_state = """  const { activeCompany, user, activeProduct, setActiveProduct } = useAuth()
  const [backupFailed, setBackupFailed] = useState(false)
  const [backupFailedDate, setBackupFailedDate] = useState('')

  useEffect(() => {
    if (user?.email !== 'crscentral.rm@gmail.com') return
    const checkBackup = () => {
      fetch('https://api.github.com/repos/crscentral/CRSAccounting/actions/workflows/nightly-backup.yml/runs?per_page=1')
        .then(r => r.json())
        .then(d => {
          if (d?.workflow_runs?.length > 0 && d.workflow_runs[0].conclusion === 'failure') {
            setBackupFailed(true)
            setBackupFailedDate(new Date(d.workflow_runs[0].created_at).toLocaleString())
          } else {
            setBackupFailed(false)
          }
        })
        .catch(() => {})
    }
    checkBackup()
    const interval = setInterval(checkBackup, 3600000)
    return () => clearInterval(interval)
  }, [user])"""

content = content.replace(old_state, new_state)

old_main = "        <main className=\"flex-1 p-3 sm:p-4 md:p-6 lg:p-8 pb-20 md:pb-8 max-w-[1600px] w-full mx-auto\">"

new_main = """        {backupFailed && (
          <div className="bg-red-600 text-white p-3 text-center text-sm font-medium shadow-md z-50 sticky top-0 flex items-center justify-center gap-2">
            <AlertTriangle size={18} />
            CRITICAL WARNING: The Nightly Database Backup failed on GitHub at {backupFailedDate}. Please check your GitHub Actions immediately.
          </div>
        )}
        <main className="flex-1 p-3 sm:p-4 md:p-6 lg:p-8 pb-20 md:pb-8 max-w-[1600px] w-full mx-auto">"""

content = content.replace(old_main, new_main)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
