import sys

def fix(filepath):
    with open(filepath, 'r') as f:
        c = f.read()
        
    c = c.replace(
        "  const [paidAmount, setPaidAmount] = useState(editingRow?.paid_amount || \\'\\')",
        "  const [paidAmount, setPaidAmount] = useState(editingRow?.paid_amount || '')"
    )

    c = c.replace(
        "  const [amount, setAmount] = useState(editingRow?.amount ?? '')",
        "  const [amount, setAmount] = useState(editingRow?.amount ?? '')\n  const [paidAmount, setPaidAmount] = useState(editingRow?.paid_amount || '')"
    )
    c = c.replace(
        "  const [amount, setAmount] = useState(editingRow?.amount || '')",
        "  const [amount, setAmount] = useState(editingRow?.amount || '')\n  const [paidAmount, setPaidAmount] = useState(editingRow?.paid_amount || '')"
    )
    
    with open(filepath, 'w') as f:
        f.write(c)
    print(f"Fixed {filepath}")

fix('src/pages/HotelExpenses.jsx')
fix('src/pages/RestaurantExpenses.jsx')
