import { useState, useEffect, useMemo } from 'react'
import {
  History,
  Search,
  Calendar,
  User,
  ChevronDown,
  ChevronUp,
  Download,
  RefreshCw,
  PlusCircle,
  Edit3,
  Trash2,
  Layers,
  ArrowRight,
  Clock,
  Eye,
  CheckCircle,
  FileSpreadsheet
} from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'

const ENTITY_LABELS = {
  hotel_guest_invoices: 'Guest Invoices',
  sales_invoices: 'Sales Invoices',
  purchase_invoices: 'Purchase Invoices',
  payment_receipts: 'Payment Receipts',
  hotel_expense_entries: 'Expense Entries',
  hotel_amc_contracts: 'AMC Contracts',
  hotel_room_stats: 'Daily Room Stats',
  restaurant_daily_revenue: 'Restaurant Revenue',
  accounts: 'Chart of Accounts',
  contacts: 'Customers & Suppliers',
  company_members: 'User Access & Members',
  hotel_expense_budget: 'Expense Budget',
  hotel_room_revenue_budget: 'Revenue Budget',
  loans_taken: 'Loans Taken',
  loan_principal_payments: 'Loan Payments',
  owner_contributions: 'Capital Contributions',
  owner_dividends: 'Owner Drawings',
  company_settings: 'Company Settings',
  app_events: 'System Events',
}

const ACTION_COLORS = {
  CREATE: {
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    icon: PlusCircle,
    label: 'Created',
  },
  UPDATE: {
    badge: 'bg-amber-50 text-amber-700 border-amber-200',
    icon: Edit3,
    label: 'Updated',
  },
  DELETE: {
    badge: 'bg-rose-50 text-rose-700 border-rose-200',
    icon: Trash2,
    label: 'Deleted',
  },
}

function formatValue(val) {
  if (val === null || val === undefined) return '—'
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'
  if (typeof val === 'object') {
    try {
      return JSON.stringify(val)
    } catch {
      return String(val)
    }
  }
  return String(val)
}

function humanizeFieldName(field) {
  return field
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
}

export default function AuditTrail() {
  const { activeCompany } = useAuth()
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  // Filters
  const [search, setSearch] = useState('')
  const [actionFilter, setActionFilter] = useState('ALL')
  const [entityFilter, setEntityFilter] = useState('ALL')
  const [userFilter, setUserFilter] = useState('ALL')
  const [timeFilter, setTimeFilter] = useState('1_year') // 'all', '1_year', '30_days', '7_days', 'today', 'custom'
  const [customStartDate, setCustomStartDate] = useState('')
  const [customEndDate, setCustomEndDate] = useState('')

  // Expanded row tracking
  const [expandedRows, setExpandedRows] = useState({})
  const [rawViewRows, setRawViewRows] = useState({})

  // Pagination
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)

  useEffect(() => {
    if (activeCompany?.id) {
      loadAuditLogs()
    }
  }, [activeCompany?.id, timeFilter, customStartDate, customEndDate])

  async function loadAuditLogs() {
    if (!activeCompany?.id) return
    setLoading(true)

    try {
      let query = supabase
        .from('audit_logs')
        .select('*')
        .eq('company_id', activeCompany.id)
        .order('created_at', { ascending: false })

      // Apply date bounds based on timeFilter
      const now = new Date()
      if (timeFilter === 'today') {
        const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString()
        query = query.gte('created_at', startOfToday)
      } else if (timeFilter === '7_days') {
        const d = new Date()
        d.setDate(d.getDate() - 7)
        query = query.gte('created_at', d.toISOString())
      } else if (timeFilter === '30_days') {
        const d = new Date()
        d.setDate(d.getDate() - 30)
        query = query.gte('created_at', d.toISOString())
      } else if (timeFilter === '1_year') {
        const d = new Date()
        d.setFullYear(d.getFullYear() - 1)
        query = query.gte('created_at', d.toISOString())
      } else if (timeFilter === 'custom') {
        if (customStartDate) query = query.gte('created_at', new Date(customStartDate).toISOString())
        if (customEndDate) {
          const end = new Date(customEndDate)
          end.setHours(23, 59, 59, 999)
          query = query.lte('created_at', end.toISOString())
        }
      }
      // 'all' doesn't restrict created_at (unlimited retention)

      const { data, error } = await query.limit(2000)
      if (error) {
        console.error('Error fetching audit logs:', error)
      } else {
        setLogs(data || [])
      }
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadAuditLogs()
  }

  const toggleRow = (id) => {
    setExpandedRows(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const toggleRaw = (id) => {
    setRawViewRows(prev => ({ ...prev, [id]: !prev[id] }))
  }

  // Extract distinct users and entities for dropdowns
  const availableUsers = useMemo(() => {
    const map = new Map()
    logs.forEach(l => {
      const email = l.user_email || 'Unknown'
      if (!map.has(email)) {
        map.set(email, l.user_name || email)
      }
    })
    return Array.from(map.entries()).map(([email, name]) => ({ email, name }))
  }, [logs])

  const availableEntities = useMemo(() => {
    const set = new Set()
    logs.forEach(l => {
      if (l.table_name) set.add(l.table_name)
    })
    return Array.from(set).sort()
  }, [logs])

  // Filtered rows
  const filteredLogs = useMemo(() => {
    const q = search.trim().toLowerCase()
    return logs.filter(log => {
      if (actionFilter !== 'ALL' && log.action !== actionFilter) return false
      if (entityFilter !== 'ALL' && log.table_name !== entityFilter) return false
      if (userFilter !== 'ALL' && log.user_email !== userFilter) return false

      if (q) {
        const matchesLabel = (log.record_label || '').toLowerCase().includes(q)
        const matchesEmail = (log.user_email || '').toLowerCase().includes(q)
        const matchesName = (log.user_name || '').toLowerCase().includes(q)
        const matchesEntity = (ENTITY_LABELS[log.table_name] || log.table_name || '').toLowerCase().includes(q)
        const matchesDiff = log.diff ? JSON.stringify(log.diff).toLowerCase().includes(q) : false
        if (!matchesLabel && !matchesEmail && !matchesName && !matchesEntity && !matchesDiff) {
          return false
        }
      }
      return true
    })
  }, [logs, actionFilter, entityFilter, userFilter, search])

  // Pagination calculation
  const totalPages = Math.max(1, Math.ceil(filteredLogs.length / pageSize))
  const paginatedLogs = useMemo(() => {
    const start = (page - 1) * pageSize
    return filteredLogs.slice(start, start + pageSize)
  }, [filteredLogs, page, pageSize])

  // KPI counters
  const stats = useMemo(() => {
    let createdCount = 0
    let updatedCount = 0
    let deletedCount = 0
    filteredLogs.forEach(l => {
      if (l.action === 'CREATE') createdCount++
      else if (l.action === 'UPDATE') updatedCount++
      else if (l.action === 'DELETE') deletedCount++
    })
    return {
      total: filteredLogs.length,
      created: createdCount,
      updated: updatedCount,
      deleted: deletedCount,
    }
  }, [filteredLogs])

  // CSV Export
  const exportToCSV = () => {
    if (!filteredLogs.length) return
    const headers = ['Timestamp', 'Action', 'Entity', 'Record Label', 'User Name', 'User Email', 'Changes Summary']
    const rows = filteredLogs.map(l => {
      let changesSummary = ''
      if (l.action === 'UPDATE' && l.diff) {
        changesSummary = Object.entries(l.diff)
          .map(([k, v]) => `${k}: ${formatValue(v.old)} -> ${formatValue(v.new)}`)
          .join('; ')
      } else if (l.action === 'CREATE') {
        changesSummary = 'New record created'
      } else if (l.action === 'DELETE') {
        changesSummary = 'Record deleted'
      }

      return [
        `"${new Date(l.created_at).toLocaleString()}"`,
        `"${l.action}"`,
        `"${ENTITY_LABELS[l.table_name] || l.table_name}"`,
        `"${(l.record_label || '').replace(/"/g, '""')}"`,
        `"${(l.user_name || '').replace(/"/g, '""')}"`,
        `"${(l.user_email || '').replace(/"/g, '""')}"`,
        `"${changesSummary.replace(/"/g, '""')}"`,
      ]
    })

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `audit_trail_${activeCompany?.name || 'company'}_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 bg-navy-50 text-navy-700 rounded-lg">
                <History size={20} />
              </div>
              <h3 className="text-base font-semibold text-slate-800">Company Audit Trail</h3>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Immutable timeline of all creations, edits, and deletions across all modules with user attribution and exact diffs.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
              Refresh
            </button>
            <button
              onClick={exportToCSV}
              disabled={filteredLogs.length === 0}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-white bg-navy-700 hover:bg-navy-800 rounded-lg shadow-sm transition-colors disabled:opacity-50"
            >
              <FileSpreadsheet size={14} />
              Export CSV
            </button>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-4 border-t border-slate-100">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <div className="text-xs text-slate-500 font-medium">Total Events</div>
            <div className="text-xl font-bold text-slate-800 mt-0.5">{stats.total}</div>
          </div>
          <div className="p-3 bg-emerald-50/60 rounded-lg border border-emerald-100">
            <div className="text-xs text-emerald-700 font-medium">Created</div>
            <div className="text-xl font-bold text-emerald-800 mt-0.5">{stats.created}</div>
          </div>
          <div className="p-3 bg-amber-50/60 rounded-lg border border-amber-100">
            <div className="text-xs text-amber-700 font-medium">Updated</div>
            <div className="text-xl font-bold text-amber-800 mt-0.5">{stats.updated}</div>
          </div>
          <div className="p-3 bg-rose-50/60 rounded-lg border border-rose-100">
            <div className="text-xs text-rose-700 font-medium">Deleted</div>
            <div className="text-xl font-bold text-rose-800 mt-0.5">{stats.deleted}</div>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Search */}
          <div className="relative lg:col-span-2">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              placeholder="Search by invoice #, guest, supplier, user, field..."
              className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-500"
            />
          </div>

          {/* Time Filter */}
          <div>
            <select
              value={timeFilter}
              onChange={e => { setTimeFilter(e.target.value); setPage(1) }}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-500 bg-white text-slate-700"
            >
              <option value="1_year">Retention: Last 1 Year (Default)</option>
              <option value="all">Retention: All Time (Unlimited)</option>
              <option value="today">Today</option>
              <option value="7_days">Last 7 Days</option>
              <option value="30_days">Last 30 Days</option>
              <option value="custom">Custom Date Range</option>
            </select>
          </div>

          {/* Action Filter */}
          <div>
            <select
              value={actionFilter}
              onChange={e => { setActionFilter(e.target.value); setPage(1) }}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-500 bg-white text-slate-700"
            >
              <option value="ALL">All Actions</option>
              <option value="CREATE">Created</option>
              <option value="UPDATE">Updated</option>
              <option value="DELETE">Deleted</option>
            </select>
          </div>

          {/* Entity Filter */}
          <div>
            <select
              value={entityFilter}
              onChange={e => { setEntityFilter(e.target.value); setPage(1) }}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-500 bg-white text-slate-700"
            >
              <option value="ALL">All Modules & Tables</option>
              {availableEntities.map(table => (
                <option key={table} value={table}>
                  {ENTITY_LABELS[table] || table}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Second row of filters: User filter & Custom Range */}
        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-100">
          <div className="w-full sm:w-64">
            <select
              value={userFilter}
              onChange={e => { setUserFilter(e.target.value); setPage(1) }}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-500 bg-white text-slate-700"
            >
              <option value="ALL">All Users</option>
              {availableUsers.map(u => (
                <option key={u.email} value={u.email}>
                  {u.name ? `${u.name} (${u.email})` : u.email}
                </option>
              ))}
            </select>
          </div>

          {timeFilter === 'custom' && (
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={customStartDate}
                onChange={e => setCustomStartDate(e.target.value)}
                className="px-2 py-1.5 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-500"
              />
              <span className="text-xs text-slate-400">to</span>
              <input
                type="date"
                value={customEndDate}
                onChange={e => setCustomEndDate(e.target.value)}
                className="px-2 py-1.5 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-500"
              />
            </div>
          )}

          <div className="ml-auto text-xs text-slate-400">
            Showing {filteredLogs.length} matching events
          </div>
        </div>
      </div>

      {/* Main Audit Trail Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400">
            <RefreshCw size={24} className="animate-spin mx-auto mb-2 text-navy-600" />
            <p className="text-sm font-medium">Loading audit history…</p>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-12 text-center">
            <History size={36} className="mx-auto text-slate-300 mb-2" />
            <h4 className="text-sm font-semibold text-slate-700">No audit logs found</h4>
            <p className="text-xs text-slate-400 mt-1">
              {search || actionFilter !== 'ALL' || entityFilter !== 'ALL' || userFilter !== 'ALL'
                ? 'Try adjusting your filters or date range.'
                : 'Activity and changes will automatically appear here as users make updates.'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {paginatedLogs.map(log => {
              const isExpanded = !!expandedRows[log.id]
              const isRaw = !!rawViewRows[log.id]
              const actionCfg = ACTION_COLORS[log.action] || {
                badge: 'bg-slate-100 text-slate-700 border-slate-200',
                icon: History,
                label: log.action,
              }
              const ActionIcon = actionCfg.icon
              const hasDiff = log.diff && Object.keys(log.diff).length > 0
              const changedFieldsCount = log.diff ? Object.keys(log.diff).length : 0

              return (
                <div key={log.id} className="transition-colors hover:bg-slate-50/60">
                  {/* Summary Bar */}
                  <div
                    onClick={() => toggleRow(log.id)}
                    className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 cursor-pointer select-none"
                  >
                    <div className="flex items-start sm:items-center gap-3">
                      {/* Action Badge */}
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border ${actionCfg.badge}`}>
                        <ActionIcon size={12} />
                        {actionCfg.label}
                      </span>

                      {/* Entity & Record Label */}
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                            {ENTITY_LABELS[log.table_name] || log.table_name}
                          </span>
                          <span className="text-sm font-semibold text-slate-800">
                            {log.record_label || `${log.table_name} #${log.record_id?.slice(0, 8)}`}
                          </span>
                        </div>

                        {log.action === 'UPDATE' && changedFieldsCount > 0 && (
                          <div className="text-xs text-slate-400 mt-0.5">
                            Modified {changedFieldsCount} field{changedFieldsCount > 1 ? 's' : ''}:{' '}
                            <span className="text-slate-600 font-medium">
                              {Object.keys(log.diff).map(humanizeFieldName).slice(0, 4).join(', ')}
                              {changedFieldsCount > 4 ? ` +${changedFieldsCount - 4} more` : ''}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* User and Timestamp */}
                    <div className="flex items-center gap-4 text-xs text-slate-500 self-end md:self-auto">
                      <div className="text-right">
                        <div className="font-medium text-slate-700 flex items-center gap-1.5 justify-end">
                          <User size={13} className="text-slate-400" />
                          {log.user_name || log.user_email || 'System'}
                        </div>
                        <div className="text-[11px] text-slate-400">{log.user_email}</div>
                      </div>

                      <div className="text-right border-l border-slate-200 pl-3 min-w-[130px]">
                        <div className="font-medium text-slate-700">
                          {new Date(log.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        </div>
                        <div className="text-[11px] text-slate-400">
                          {new Date(log.created_at).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </div>
                      </div>

                      <div className="text-slate-400">
                        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Detail Panel */}
                  {isExpanded && (
                    <div className="px-4 pb-4 pt-1 bg-slate-50/90 border-t border-slate-100 text-xs">
                      <div className="flex items-center justify-between mb-3 pt-2">
                        <div className="font-semibold text-slate-700 flex items-center gap-1.5">
                          <span>Change Details</span>
                          <span className="text-slate-400 font-normal">
                            (Record ID: <code className="bg-white px-1.5 py-0.5 rounded border border-slate-200 text-[11px]">{log.record_id || 'N/A'}</code>)
                          </span>
                        </div>

                        <button
                          onClick={(e) => { e.stopPropagation(); toggleRaw(log.id) }}
                          className="text-[11px] font-medium text-navy-600 hover:text-navy-800 bg-white px-2 py-1 rounded border border-slate-200"
                        >
                          {isRaw ? 'Show Formatted Diff' : 'View Raw JSON'}
                        </button>
                      </div>

                      {isRaw ? (
                        <div className="bg-slate-900 text-slate-100 p-3 rounded-lg overflow-x-auto font-mono text-[11px] max-h-72">
                          <pre>{JSON.stringify({ diff: log.diff, old: log.old_data, new: log.new_data }, null, 2)}</pre>
                        </div>
                      ) : (
                        <div>
                          {log.action === 'UPDATE' && hasDiff ? (
                            <div className="border border-slate-200 rounded-lg overflow-hidden bg-white">
                              <table className="w-full text-left border-collapse">
                                <thead>
                                  <tr className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-semibold text-[11px]">
                                    <th className="py-2 px-3 w-1/4">Field</th>
                                    <th className="py-2 px-3 w-3/8 text-rose-700 bg-rose-50/40">Previous Value</th>
                                    <th className="py-2 px-3 w-3/8 text-emerald-700 bg-emerald-50/40">New Value</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                  {Object.entries(log.diff).map(([key, val]) => (
                                    <tr key={key} className="hover:bg-slate-50/50">
                                      <td className="py-2 px-3 font-medium text-slate-700">
                                        {humanizeFieldName(key)}
                                        <div className="text-[10px] font-mono text-slate-400">{key}</div>
                                      </td>
                                      <td className="py-2 px-3 text-rose-800 bg-rose-50/20 break-all font-mono text-[11px]">
                                        <span className="line-through opacity-80">{formatValue(val.old)}</span>
                                      </td>
                                      <td className="py-2 px-3 text-emerald-800 bg-emerald-50/20 break-all font-mono text-[11px]">
                                        <span className="font-semibold">{formatValue(val.new)}</span>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          ) : log.action === 'CREATE' ? (
                            <div className="bg-white border border-slate-200 rounded-lg p-3">
                              <div className="text-emerald-700 font-semibold mb-2 flex items-center gap-1">
                                <PlusCircle size={13} />
                                Record Created Successfully
                              </div>
                              {log.new_data ? (
                                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                                  {Object.entries(log.new_data)
                                    .filter(([k]) => !['id', 'company_id', 'created_at', 'updated_at'].includes(k) && log.new_data[k] !== null)
                                    .slice(0, 12)
                                    .map(([k, v]) => (
                                      <div key={k} className="p-2 bg-slate-50 rounded border border-slate-100">
                                        <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">{humanizeFieldName(k)}</div>
                                        <div className="font-medium text-slate-700 mt-0.5 truncate">{formatValue(v)}</div>
                                      </div>
                                    ))}
                                </div>
                              ) : (
                                <p className="text-slate-500">Record inserted into {ENTITY_LABELS[log.table_name] || log.table_name}.</p>
                              )}
                            </div>
                          ) : log.action === 'DELETE' ? (
                            <div className="bg-white border border-slate-200 rounded-lg p-3">
                              <div className="text-rose-700 font-semibold mb-2 flex items-center gap-1">
                                <Trash2 size={13} />
                                Record Deleted
                              </div>
                              {log.old_data ? (
                                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                                  {Object.entries(log.old_data)
                                    .filter(([k]) => !['id', 'company_id', 'created_at', 'updated_at'].includes(k) && log.old_data[k] !== null)
                                    .slice(0, 9)
                                    .map(([k, v]) => (
                                      <div key={k} className="p-2 bg-rose-50/30 rounded border border-rose-100">
                                        <div className="text-[10px] text-rose-500 font-medium uppercase tracking-wider">{humanizeFieldName(k)}</div>
                                        <div className="font-medium text-slate-700 mt-0.5 truncate">{formatValue(v)}</div>
                                      </div>
                                    ))}
                                </div>
                              ) : (
                                <p className="text-slate-500">Record removed from {ENTITY_LABELS[log.table_name] || log.table_name}.</p>
                              )}
                            </div>
                          ) : (
                            <div className="bg-white border border-slate-200 rounded-lg p-3 text-slate-600">
                              Event logged: {log.record_label}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* Pagination Controls */}
        {filteredLogs.length > 0 && (
          <div className="p-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-50/50">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span>Rows per page:</span>
              <select
                value={pageSize}
                onChange={e => { setPageSize(Number(e.target.value)); setPage(1) }}
                className="px-2 py-1 text-xs border border-slate-200 rounded bg-white"
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <span className="ml-2">
                Showing {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, filteredLogs.length)} of {filteredLogs.length} events
              </span>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 text-xs border border-slate-200 rounded bg-white hover:bg-slate-50 text-slate-700 disabled:opacity-40"
              >
                Previous
              </button>
              <span className="text-xs text-slate-600 px-2 font-medium">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 text-xs border border-slate-200 rounded bg-white hover:bg-slate-50 text-slate-700 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
