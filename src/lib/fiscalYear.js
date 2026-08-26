// All date math here works in plain calendar terms (UTC-safe ISO strings).

export const MONTH_NAMES = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December'
]

export const PERIOD_TYPES = [
  { value: 'MTD', label: 'MTD (This Month)' },
  { value: 'YTD', label: 'YTD' },
  { value: 'LAST_N_YEARS', label: 'Last N Years' },
  { value: 'NEXT_N_YEARS', label: 'Next N Years' },
  { value: 'CUSTOM', label: 'Custom Range' },
  { value: 'ALL_TIME', label: 'All Time' },
]

function ymd(d) {
  return d.toISOString().slice(0, 10)
}

/** Returns { from, to } for one specific calendar month. If that month is the current
 * month, `to` is today (same MTD behaviour as before); otherwise `to` is the last day
 * of that month. */
export function getMonthRange(year, month, today = new Date()) {
  const from = new Date(Date.UTC(year, month - 1, 1))
  const isCurrentMonth = today.getUTCFullYear() === year && (today.getUTCMonth() + 1) === month
  const to = isCurrentMonth ? today : new Date(Date.UTC(year, month, 0))
  return { from: ymd(from), to: ymd(to) }
}

/** Returns { from, to } for the current month-to-date. */
export function getMTDRange(today = new Date()) {
  const from = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1))
  return { from: ymd(from), to: ymd(today) }
}

/**
 * Returns { from, to } for Year-To-Date, respecting a custom fiscal year start month
 * (1 = January/calendar year, 4 = April-start like India, 9 = Sept-start, etc).
 */
export function getYTDRange(fiscalYearStartMonth = 1, today = new Date()) {
  const y = today.getUTCFullYear()
  const m = today.getUTCMonth() + 1 // 1-12
  let startYear = y
  if (m < fiscalYearStartMonth) startYear = y - 1
  const from = new Date(Date.UTC(startYear, fiscalYearStartMonth - 1, 1))
  return { from: ymd(from), to: ymd(today) }
}

/** Returns { from, to } for the last N full fiscal years plus current partial year. */
export function getLastNYearsRange(n, fiscalYearStartMonth = 1, today = new Date()) {
  const y = today.getUTCFullYear()
  const m = today.getUTCMonth() + 1
  let currentFYStartYear = m < fiscalYearStartMonth ? y - 1 : y
  const fromYear = currentFYStartYear - (n - 1)
  const from = new Date(Date.UTC(fromYear, fiscalYearStartMonth - 1, 1))
  return { from: ymd(from), to: ymd(today) }
}

/** Returns { from, to } for the next N fiscal years starting from today (for forecasts). */
export function getNextNYearsRange(n, fiscalYearStartMonth = 1, today = new Date()) {
  const y = today.getUTCFullYear()
  const m = today.getUTCMonth() + 1
  let currentFYStartYear = m < fiscalYearStartMonth ? y - 1 : y
  const toYear = currentFYStartYear + n
  const to = new Date(Date.UTC(toYear, fiscalYearStartMonth - 1, 0)) // day before next FY starts
  return { from: ymd(today), to: ymd(to) }
}

export function resolvePeriodRange(periodType, opts = {}) {
  const { fiscalYearStartMonth = 1, n = 1, customFrom, customTo, today = new Date(), year, month } = opts
  switch (periodType) {
    case 'MTD': return getMonthRange(year || today.getUTCFullYear(), month || (today.getUTCMonth() + 1), today)
    case 'YTD': return getYTDRange(fiscalYearStartMonth, today)
    case 'LAST_N_YEARS': return getLastNYearsRange(n, fiscalYearStartMonth, today)
    case 'NEXT_N_YEARS': return getNextNYearsRange(n, fiscalYearStartMonth, today)
    case 'CUSTOM': return { from: customFrom, to: customTo }
    case 'ALL_TIME':
    default:
      return { from: '1970-01-01', to: ymd(today) }
  }
}

/**
 * Adapter for the ReportOptionsModal's simplified period values (MTD/YTD/LAST_1_YEAR/
 * LAST_3_YEARS/CUSTOM/ALL_TIME) -> an actual { from, to } date range.
 */
export function resolveReportPeriod(periodValue, fiscalYearStartMonth = 1, customFrom, customTo) {
  switch (periodValue) {
    case 'MTD': return resolvePeriodRange('MTD')
    case 'YTD': return resolvePeriodRange('YTD', { fiscalYearStartMonth })
    case 'LAST_1_YEAR': return resolvePeriodRange('LAST_N_YEARS', { n: 1, fiscalYearStartMonth })
    case 'LAST_3_YEARS': return resolvePeriodRange('LAST_N_YEARS', { n: 3, fiscalYearStartMonth })
    case 'CUSTOM': return { from: customFrom, to: customTo }
    case 'ALL_TIME':
    default:
      return resolvePeriodRange('ALL_TIME')
  }
}
