import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    """      {years.map(year => activeProduct === 'hotel' ? (""",
    """      {activeProduct === 'hotel' && years.map(year => ("""
)
content = content.replace(
    """      ) : null)}""",
    """      ))}"""
)
content = content.replace(
    """      <div className="mt-12 pt-8 border-t border-slate-200">""",
    """      <div className={activeProduct === 'hotel' ? "mt-12 pt-8 border-t border-slate-200" : ""}>"""
)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
