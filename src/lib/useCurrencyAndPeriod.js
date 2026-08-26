import { useState, useEffect, useCallback } from 'react'
import { useAuth } from './AuthContext'
import { ensureTodayRatesCached, getLatestRatesMap, convertFromUsd, formatMoney } from './fx'
import { resolvePeriodRange } from './fiscalYear'
import { CURRENCY_LIST } from './currencies'

export function useCurrencyAndPeriod() {
  const { activeCompany } = useAuth()
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [ratesMap, setRatesMap] = useState({ USD: 1 })
  const [periodType, setPeriodType] = useState('MTD')
  const [n, setN] = useState(1)
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)
  const [fyStartMonth, setFyStartMonth] = useState(activeCompany?.fiscal_year_start_month || 1)
  const [customRange, setCustomRange] = useState({ from: null, to: null })

  useEffect(() => {
    if (activeCompany?.fiscal_year_start_month) setFyStartMonth(activeCompany.fiscal_year_start_month)
  }, [activeCompany])

  useEffect(() => {
    ensureTodayRatesCached().then(refreshRates)
  }, [])

  const refreshRates = useCallback(async () => {
    const codes = CURRENCY_LIST.map(c => c.code)
    const map = await getLatestRatesMap(codes)
    setRatesMap(map)
  }, [])

  useEffect(() => { refreshRates() }, [displayCurrency, refreshRates])

  const range = resolvePeriodRange(periodType, {
    fiscalYearStartMonth: fyStartMonth,
    n,
    customFrom: customRange.from,
    customTo: customRange.to,
    year: selectedYear,
    month: selectedMonth,
  })

  const convert = useCallback((amountUsd) => convertFromUsd(amountUsd, displayCurrency, ratesMap), [displayCurrency, ratesMap])
  const fmt = useCallback((amountUsd) => formatMoney(convert(amountUsd), displayCurrency), [convert, displayCurrency])

  return {
    displayCurrency, setDisplayCurrency,
    currencyProps: { value: displayCurrency, onChange: setDisplayCurrency },
    periodProps: {
      periodType, onPeriodTypeChange: setPeriodType,
      n, onNChange: setN,
      fiscalYearStartMonth: fyStartMonth, onFiscalYearStartMonthChange: setFyStartMonth,
      customFrom: customRange.from, customTo: customRange.to,
      onCustomChange: setCustomRange,
      selectedYear, selectedMonth,
      onYearMonthChange: ({ year, month }) => { setSelectedYear(year); setSelectedMonth(month) },
    },
    range,
    convert,
    fmt,
    ratesMap,
  }
}
