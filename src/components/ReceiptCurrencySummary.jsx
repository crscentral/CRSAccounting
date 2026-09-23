import { useState, useEffect } from 'react'
import { DollarSign, RefreshCw } from 'lucide-react'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'

export default function ReceiptCurrencySummary({ receipts }) {
  const cp = useCurrencyAndPeriod()

  const [rates, setRates] = useState({})
  
  // Aggregate receipts by currency
  const byCurrency = {}
  let totalUsdDefault = 0
  
  receipts.forEach(r => {
    byCurrency[r.currency] = byCurrency[r.currency] || { count: 0, native: 0, usd: 0 }
    byCurrency[r.currency].count += 1
    byCurrency[r.currency].native += Number(r.amount)
    byCurrency[r.currency].usd += Number(r.amount_usd)
    totalUsdDefault += Number(r.amount_usd)
  })

  // Initialize rates based on weighted average of locked rates
  useEffect(() => {
    const initialRates = {}
    Object.entries(byCurrency).forEach(([code, data]) => {
      if (code === 'USD') initialRates[code] = 1
      else if (data.usd > 0) initialRates[code] = data.native / data.usd
      else initialRates[code] = 1
    })
    setRates(initialRates)
  }, [receipts])

  const handleRateChange = (code, val) => {
    setRates(prev => ({ ...prev, [code]: Number(val) || prev[code] }))
  }

  const resetRates = () => {
    const initialRates = {}
    Object.entries(byCurrency).forEach(([code, data]) => {
      if (code === 'USD') initialRates[code] = 1
      else if (data.usd > 0) initialRates[code] = data.native / data.usd
      else initialRates[code] = 1
    })
    setRates(initialRates)
  }

  const currencies = Object.entries(byCurrency)
  
  let grandTotalUsd = 0

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2 text-emerald-600">
          <DollarSign size={20} />
          <h3 className="font-bold text-slate-800 text-lg">Receipt Currency Summary</h3>
        </div>
        <button onClick={resetRates} className="flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-800">
          <RefreshCw size={15} /> Refresh Rates
        </button>
      </div>

      <div className="space-y-4">
        {currencies.map(([code, data]) => {
          const currentRate = rates[code] || 1
          const computedUsd = code === 'USD' ? data.native : data.native / currentRate
          grandTotalUsd += computedUsd

          return (
            <div key={code} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-slate-50/50 rounded-lg border border-slate-100 gap-4">
              <div className="flex items-center gap-4">
                <span className="px-3 py-1 rounded bg-blue-100 text-blue-700 font-bold text-sm shrink-0">{code}</span>
                <div>
                  <div className="font-bold text-slate-800 text-base">{Number(data.native).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{data.count} receipt(s)</div>
                </div>
              </div>
              
              <div className="flex items-center gap-6 sm:gap-12 justify-between sm:justify-end">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-slate-400">Rate (per USD):</span>
                  <input 
                    type="number" 
                    step="0.0001"
                    value={rates[code] !== undefined ? Number(rates[code]).toFixed(2).replace(/\.?0+$/, '') : ''} 
                    onChange={e => handleRateChange(code, e.target.value)}
                    className="w-24 px-2 py-1 text-sm border border-slate-200 rounded text-center focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                    disabled={code === 'USD'}
                  />
                </div>
                <div className="text-right shrink-0 min-w-[100px]">
                  <div className="font-bold text-emerald-600">{cp.fmt(computedUsd)}</div>
                  <div className="text-[10px] text-slate-400 font-medium mt-0.5">in USD</div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-6 p-5 rounded-lg border border-emerald-200 bg-emerald-50/50 flex items-center justify-between">
        <div>
          <div className="font-bold text-emerald-800 text-lg">Grand Total (USD)</div>
          <div className="text-xs font-medium text-emerald-600/80 mt-0.5">{currencies.length} currencies consolidated</div>
        </div>
        <div className="font-bold text-emerald-600 text-2xl">
          {cp.fmt(grandTotalUsd)}
        </div>
      </div>
    </div>
  )
}
