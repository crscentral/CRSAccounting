with open('src/components/KpiCard.jsx', 'r') as f:
    content = f.read()

content = content.replace('text-slate-500 truncate"', 'text-slate-500 line-clamp-2 leading-snug break-words"')

with open('src/components/KpiCard.jsx', 'w') as f:
    f.write(content)
