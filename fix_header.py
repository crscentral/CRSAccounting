with open('src/components/PageHeader.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    '<div className="mb-5 sm:mb-6">',
    '<div className="sticky top-0 z-[10] bg-slate-50 py-4 -mt-4 mb-2 sm:mb-3">'
)

with open('src/components/PageHeader.jsx', 'w') as f:
    f.write(content)
