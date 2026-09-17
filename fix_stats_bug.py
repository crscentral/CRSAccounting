import re

with open('src/pages/HotelOccupancyStats.jsx', 'r') as f:
    code = f.read()

old_loadAll = """  async function loadAll() {
    setLoading(true)
    
    const [{ data: settings }, { data: statRows }, { data: budgetRows }, { data: accounts }, { data: entries }] = await Promise.all(["""

new_loadAll = """  async function loadAll() {
    setLoading(true)
    const range = rangeFor(view)
    
    const [{ data: settings }, { data: statRows }, { data: budgetRows }, { data: accounts }, { data: entries }] = await Promise.all(["""

code = code.replace(old_loadAll, new_loadAll)

with open('src/pages/HotelOccupancyStats.jsx', 'w') as f:
    f.write(code)
