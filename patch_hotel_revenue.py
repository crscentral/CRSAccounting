import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

old_kpis = r"""<KpiCard label="Room Revenue" value=\{cp\.fmt\(totalRoomRevenue\)\} tone="green" />
        <KpiCard label="Room Revenue Collected" value=\{cp\.fmt\(totalCollected\)\} tone="blue" />
        <KpiCard label="Ancillary Revenue" value=\{cp\.fmt\(totalAncillary\)\} tone="gold" />"""

new_kpis = """<KpiCard label="Total Daily Revenue" value={cp.fmt(totalRoomRevenue + totalAncillary)} tone="slate" />
        <KpiCard label="Room Revenue" value={cp.fmt(totalRoomRevenue)} tone="green" />
        <KpiCard label="Room Rev. Collected" value={cp.fmt(totalCollected)} tone="blue" />
        <KpiCard label="Ancillary Revenue" value={cp.fmt(totalAncillary)} tone="gold" />"""

# Also update the grid cols to 4
old_grid = r'<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">'
new_grid = '<div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">'

code = re.sub(old_kpis, new_kpis, code)
code = re.sub(old_grid, new_grid, code)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
