import re

with open('src/components/PaymentReceiptFormModal.jsx', 'r') as f:
    content = f.read()

# Make sure currency change also clears fxRate
content = re.sub(r'onChange=\{e => setCurrency\(e\.target\.value\)\}', 
                 r"onChange={e => { setCurrency(e.target.value); if(e.target.value === 'USD') setFxRate(''); }}", content)

# Add the Conversion Rate block right after the Currency select field (after `</div>` for grid)
old_grid_end = """              {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
            </select>
          </Field>
        </div>"""

new_grid_end = """              {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
            </select>
          </Field>
        </div>
        
        {currency !== 'USD' && (
          <div className="mt-2 pt-2">
            <Field label="Conversion Rate (to USD) - Optional">
              <input type="number" step="0.0001" placeholder="Auto-fetch live rate" value={fxRate} onChange={e => setFxRate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none" />
            </Field>
          </div>
        )}"""
        
if "Conversion Rate (to USD)" not in content:
    content = content.replace(old_grid_end, new_grid_end)

with open('src/components/PaymentReceiptFormModal.jsx', 'w') as f:
    f.write(content)

