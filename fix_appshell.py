with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

content = content.replace("import { useState } from 'react'", "import { useState, useEffect } from 'react'")

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
