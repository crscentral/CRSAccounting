import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# 1. Update imports
import_target = "import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts'"
import_replacement = "import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'"
content = content.replace(import_target, import_replacement)

# 2. Add totalRevenue state
state_target = "const [entries, setEntries] = useState([]);"
state_replacement = "const [entries, setEntries] = useState([]);\n  const [totalRevenue, setTotalRevenue] = useState(0);"
content = content.replace(state_target, state_replacement)

# 3. Modify loadAll
load_all_target = """const [{ data: exp }, { data: amc }, { data: accs }, { data: settings }, { data: roomStats }, { data: pi }, { data: cont }] = await Promise.all([
      supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to).order('expense_date', { ascending: false }),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).order('created_at', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype, type').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code'),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_stats').select('rooms_occupied').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to),
      supabase.from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name')
    ])
    setEntries(exp || [])"""

load_all_replacement = """const [{ data: exp }, { data: amc }, { data: accs }, { data: settings }, { data: roomStats }, { data: pi }, { data: cont }, { data: hre }, { data: rdr }] = await Promise.all([
      supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to).order('expense_date', { ascending: false }),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).order('created_at', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype, type').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code'),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_stats').select('rooms_occupied, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to),
      supabase.from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name'),
      supabase.from('hotel_revenue_entries').select('amount_usd').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      supabase.from('restaurant_daily_revenue').select('total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
    ])
    
    let rev = 0;
    (roomStats || []).forEach(r => rev += Number(r.room_revenue_usd) || 0);
    (hre || []).forEach(r => rev += Number(r.amount_usd) || 0);
    (rdr || []).forEach(r => {
       const total = Number(r.total_amount_usd) || ((Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0))
       if (total > 0) rev += total;
    });
    setTotalRevenue(rev);
    setEntries(exp || [])"""

content = content.replace(load_all_target, load_all_replacement)


# 4. Generate data for BarCharts
pie_data_target = """const pieData = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => ({ 
    name, 
    value,
    percentStr: totalExpenses > 0 ? ((value / totalExpenses) * 100).toFixed(1) + '%' : '0.0%'
  })).sort((a, b) => b.value - a.value)"""

pie_data_replacement = pie_data_target + """
  const barDataRev = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => ({
    name: name.split(' - ')[1] || name,
    fullName: name,
    value: value,
    percentStr: totalRevenue > 0 ? ((value / totalRevenue) * 100).toFixed(1) + '%' : '0.0%'
  })).sort((a, b) => b.value - a.value)

  const barDataExp = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => ({
    name: name.split(' - ')[1] || name,
    fullName: name,
    value: value,
    percentStr: totalExpenses > 0 ? ((value / totalExpenses) * 100).toFixed(1) + '%' : '0.0%'
  })).sort((a, b) => b.value - a.value)
  
  const totalRevPercent = totalRevenue > 0 ? ((totalExpenses / totalRevenue) * 100).toFixed(1) + '%' : '0.0%';
  const totalExpPercent = '100.0%';
"""

content = content.replace(pie_data_target, pie_data_replacement)

# 5. Add the JSX for the new charts
chart_target = """                <Legend layout="vertical" verticalAlign="middle" align="right" content={renderCustomLegend} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>"""

chart_replacement = chart_target + """
      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex justify-between items-start mb-4">
             <h3 className="text-sm font-semibold text-slate-800">Expense % compared to Revenue Generated</h3>
             <div className="text-right text-xs">
               <div className="text-slate-500 font-medium">Total Revenue</div>
               <div className="font-bold text-slate-700">{cp.fmt(totalRevenue)}</div>
             </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barDataRev} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <RechartsTooltip formatter={(value, name, props) => [`${cp.fmt(value)} (${props.payload.percentStr})`, 'Amount']} labelFormatter={(label) => label} cursor={{fill: 'transparent'}} />
                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={16}>
                  {barDataRev.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-sm font-semibold">
             <span className="text-slate-600">Total Expenses</span>
             <span className="text-slate-800">{cp.fmt(totalExpenses)} <span className="text-blue-600 ml-1">({totalRevPercent})</span></span>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex justify-between items-start mb-4">
             <h3 className="text-sm font-semibold text-slate-800">Expense % compared to Total Expense</h3>
             <div className="text-right text-xs">
               <div className="text-slate-500 font-medium">Total Expenses</div>
               <div className="font-bold text-slate-700">{cp.fmt(totalExpenses)}</div>
             </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barDataExp} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <RechartsTooltip formatter={(value, name, props) => [`${cp.fmt(value)} (${props.payload.percentStr})`, 'Amount']} labelFormatter={(label) => label} cursor={{fill: 'transparent'}} />
                <Bar dataKey="value" fill="#f59e0b" radius={[0, 4, 4, 0]} barSize={16}>
                  {barDataExp.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-sm font-semibold">
             <span className="text-slate-600">Total Expenses</span>
             <span className="text-slate-800">{cp.fmt(totalExpenses)} <span className="text-amber-600 ml-1">({totalExpPercent})</span></span>
          </div>
        </div>
      </div>"""

content = content.replace(chart_target, chart_replacement)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)

