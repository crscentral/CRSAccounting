import re

def patch():
    with open('src/pages/HotelExpenses.jsx', 'r') as f:
        content = f.read()

    # 1. Update pieData
    old_pie_data = "const pieData = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value)"
    new_pie_data = """const pieData = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => ({ 
    name, 
    value,
    percentStr: totalExpenses > 0 ? ((value / totalExpenses) * 100).toFixed(1) + '%' : '0.0%'
  })).sort((a, b) => b.value - a.value)
  
  const renderCustomLegend = (props) => {
    const { payload } = props;
    return (
      <ul className="text-[11px] space-y-1.5 w-full">
        {payload.map((entry, index) => (
          <li key={`item-${index}`} className="flex items-center">
            <span className="w-10 text-right mr-2 text-slate-500 font-medium shrink-0">{entry.payload.percentStr}</span>
            <span className="w-2.5 h-2.5 mr-2 rounded-[2px] shrink-0" style={{ backgroundColor: entry.color }}></span>
            <span style={{ color: entry.color }} className="truncate max-w-[160px]" title={entry.value}>{entry.value}</span>
          </li>
        ))}
      </ul>
    );
  }"""
    
    if old_pie_data in content:
        content = content.replace(old_pie_data, new_pie_data)
        print("Patched pieData and added renderCustomLegend")
    else:
        print("Could not find old pieData block")
        
    # 2. Update Legend tags
    old_legend = '<Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ fontSize: \'11px\' }} />'
    new_legend = '<Legend layout="vertical" verticalAlign="middle" align="right" content={renderCustomLegend} />'
    
    if old_legend in content:
        content = content.replace(old_legend, new_legend)
        print("Patched Legend components")
    else:
        print("Could not find old Legend tag")
        
    with open('src/pages/HotelExpenses.jsx', 'w') as f:
        f.write(content)

patch()
