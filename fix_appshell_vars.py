with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

old_state = "  const { companies, activeCompany, switchCompany, signOut, activeRole, activeProduct, availableProducts, switchProduct } = useAuth()"
new_state = """  const { companies, activeCompany, switchCompany, signOut, activeRole, activeProduct, availableProducts, switchProduct, user } = useAuth()
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

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)

