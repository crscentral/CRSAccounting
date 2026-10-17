import { supabase } from './supabaseClient'

/**
 * Log an audit event to the audit_logs table.
 * Most database mutations are automatically captured by PostgreSQL triggers.
 * This helper can be used to log application-level events (e.g., exports, backups, invites).
 */
export async function logAuditEvent({
  companyId,
  tableName = 'app_events',
  recordId = null,
  recordLabel,
  action = 'EVENT',
  userEmail = null,
  userName = null,
  oldData = null,
  newData = null,
  diff = null,
}) {
  try {
    if (!companyId) return
    const { data: { user } } = await supabase.auth.getUser()
    const email = userEmail || user?.email || 'Unknown'
    const name = userName || user?.user_metadata?.full_name || email

    await supabase.from('audit_logs').insert({
      company_id: companyId,
      table_name: tableName,
      record_id: recordId ? String(recordId) : null,
      record_label: recordLabel,
      action,
      user_id: user?.id || null,
      user_email: email,
      user_name: name,
      old_data: oldData,
      new_data: newData,
      diff,
      created_at: new Date().toISOString(),
    })
  } catch (err) {
    console.warn('Failed to record audit log:', err)
  }
}
