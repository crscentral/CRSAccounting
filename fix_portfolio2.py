import re

with open('src/pages/PortfolioDashboard.jsx', 'r') as f:
    code = f.read()

bad_destructure = "const [{ data: accounts }, { data: entries }, { data: salesInv }, { data: receipts }, { data: hotelSettings }, { data: hotelStats }] = await Promise.all(["
good_destructure = "const [{ data: hotelSettings }, { data: hotelStats }, { data: accounts }, { data: entries }, { data: salesInv }, { data: receipts }] = await Promise.all(["

code = code.replace(bad_destructure, good_destructure)

with open('src/pages/PortfolioDashboard.jsx', 'w') as f:
    f.write(code)
