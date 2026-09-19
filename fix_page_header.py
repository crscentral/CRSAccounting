import re

with open('src/components/PageHeader.jsx', 'r') as f:
    code = f.read()

# Make the outer container wrap more gracefully so it doesn't force 2 lines if it can fit, 
# and reduce the gap to save horizontal space.
old_outer = '      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">'
new_outer = '      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between flex-wrap">'
code = code.replace(old_outer, new_outer)

old_inner = '        <div className="flex flex-col sm:flex-row gap-2 sm:items-center">'
new_inner = '        <div className="flex flex-col sm:flex-row gap-1.5 sm:items-center flex-wrap justify-end">'
code = code.replace(old_inner, new_inner)

with open('src/components/PageHeader.jsx', 'w') as f:
    f.write(code)
