files = [
    'src/pages/Dashboard.jsx',
    'src/pages/HistoricalImport.jsx',
    'src/pages/HotelOccupancyStats.jsx'
]

for path in files:
    with open(path, 'r') as f:
        content = f.read()
    
    if "import { getLocalDate } from" not in content:
        content = content.replace("import ", "import { getLocalDate } from '../lib/dateUtils'\nimport ", 1)
        with open(path, 'w') as f:
            f.write(content)
