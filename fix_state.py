import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

old_state = r"const \[hotelAmc, setHotelAmc\] = useState\(\[\]\)"
new_state = """const [hotelAmc, setHotelAmc] = useState([])
  const [hotelRevenueEntries, setHotelRevenueEntries] = useState([])"""
code = re.sub(old_state, new_state, code)

old_set = r"setHotelAmc\(hamc \|\| \[\]\)"
new_set = """setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])"""
code = re.sub(old_set, new_set, code)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
