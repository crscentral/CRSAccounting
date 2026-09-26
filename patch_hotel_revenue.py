import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

old_states = """  const [roomStats, setRoomStats] = useState([])
  const [ancillary, setAncillary] = useState([])
  const [revenueAccounts, setRevenueAccounts] = useState([])
  const [totalRooms, setTotalRooms] = useState(0)
  const [restRevenue, setRestRevenue] = useState([])"""

new_states = """  const [roomStats, setRoomStats] = useState([])
  const [ancillary, setAncillary] = useState([])
  const [ancRoom, setAncRoom] = useState([])
  const [ancFB, setAncFB] = useState([])
  const [ancOther, setAncOther] = useState([])
  const [revenueAccounts, setRevenueAccounts] = useState([])
  const [totalRooms, setTotalRooms] = useState(0)
  const [restRevenue, setRestRevenue] = useState([])"""

content = content.replace(old_states, new_states)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
