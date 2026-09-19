import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "import { useEffect, useState, useMemo } from 'react'",
    "import React, { useEffect, useState, useMemo } from 'react'"
)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
