with open('src/components/RestaurantRevenueFormModal.jsx', 'r') as f:
    content = f.read()

# Change the logic for collected
old_logic = "const balance = total - (Number(collected) || 0)"
new_logic = "const actualCollected = collected === '' ? total : (Number(collected) || 0)\n  const balance = total - actualCollected"
content = content.replace(old_logic, new_logic)

old_submit = "collected: Number(collected) || 0,"
new_submit = "collected: actualCollected,"
content = content.replace(old_submit, new_submit)

old_submit_usd = "collected_usd: Math.round((Number(collected) || 0) / fxRate * 100) / 100,"
new_submit_usd = "collected_usd: Math.round(actualCollected / fxRate * 100) / 100,"
content = content.replace(old_submit_usd, new_submit_usd)

old_input = "placeholder={`Defaults to 0`} />"
new_input = "placeholder={`Defaults to Full Total (${total.toFixed(2)})`} />"
content = content.replace(old_input, new_input)

old_render = "Collected: <strong className=\"text-emerald-600\">{(Number(collected)||0).toFixed(2)} {currency}</strong>"
new_render = "Collected: <strong className=\"text-emerald-600\">{actualCollected.toFixed(2)} {currency}</strong>"
content = content.replace(old_render, new_render)

with open('src/components/RestaurantRevenueFormModal.jsx', 'w') as f:
    f.write(content)

