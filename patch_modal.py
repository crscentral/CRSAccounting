import re

with open('src/components/RestaurantRevenueFormModal.jsx', 'r') as f:
    content = f.read()

# 1. Add state for collected
content = content.replace(
    "const [otherAmount, setOtherAmount] = useState(entry?.other_amount ?? 0)",
    "const [otherAmount, setOtherAmount] = useState(entry?.other_amount ?? 0)\n  const [collected, setCollected] = useState(entry?.collected ?? '')"
)

# 2. Add calculation for balance
content = content.replace(
    "const perCover = covers > 0 ? total / covers : 0",
    "const perCover = covers > 0 ? total / covers : 0\n  const balance = total - (Number(collected) || 0)"
)

# 3. Add to payload
old_payload = """        other_amount_usd: Math.round((Number(otherAmount) || 0) / fxRate * 100) / 100,
        amount_usd: Math.round(total / fxRate * 100) / 100,"""
new_payload = """        other_amount_usd: Math.round((Number(otherAmount) || 0) / fxRate * 100) / 100,
        amount_usd: Math.round(total / fxRate * 100) / 100,
        collected: Number(collected) || 0,
        collected_usd: Math.round((Number(collected) || 0) / fxRate * 100) / 100,"""
content = content.replace(old_payload, new_payload)

# 4. Add UI field
old_grid = """        <div className="grid grid-cols-3 gap-3">
          <Field label="Food Revenue">"""
new_grid = """        <div className="grid grid-cols-3 gap-3">
          <Field label="Food Revenue">"""
# Actually, let's put "Amount Collected" in its own row below the 3 revenues.
old_total_box = """        <div className="bg-slate-50 rounded-lg p-3 flex items-center justify-between text-sm">
          <span className="text-slate-500">Total: <strong className="text-slate-700">{total.toFixed(2)} {currency}</strong></span>
          <span className="text-slate-500">Revenue / Cover: <strong className="text-slate-700">{perCover.toFixed(2)} {currency}</strong></span>
        </div>"""
new_total_box = """        <Field label="Amount Collected (Optional)">
          <input type="number" step="0.01" min="0" value={collected} onChange={e => setCollected(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder={`Defaults to 0`} />
        </Field>

        <div className="bg-slate-50 rounded-lg p-3 flex flex-col gap-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-500">Total Rev: <strong className="text-slate-700">{total.toFixed(2)} {currency}</strong></span>
            <span className="text-slate-500">Rev/Cover: <strong className="text-slate-700">{perCover.toFixed(2)} {currency}</strong></span>
          </div>
          <div className="flex items-center justify-between border-t border-slate-200 pt-2">
            <span className="text-slate-500">Collected: <strong className="text-emerald-600">{(Number(collected)||0).toFixed(2)} {currency}</strong></span>
            <span className="text-slate-500">Balance: <strong className={balance > 0 ? "text-red-600" : "text-slate-700"}>{balance.toFixed(2)} {currency}</strong></span>
          </div>
        </div>"""
content = content.replace(old_total_box, new_total_box)

with open('src/components/RestaurantRevenueFormModal.jsx', 'w') as f:
    f.write(content)
