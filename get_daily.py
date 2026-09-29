import re

def main():
    with open('src/pages/HotelExpenses.jsx', 'r') as f:
        content = f.read()

    # Find the entire block for activeTab === 'daily'
    match = re.search(r"(\{activeTab === 'daily' && \(\n\s*<>\n\s*<div className=\"flex justify-between items-end mb-3\">.*?)(?=\{activeTab === 'purchase' && \()", content, re.DOTALL)
    if match:
        daily_block = match.group(1)
        with open('daily_block.txt', 'w') as f:
            f.write(daily_block)
            
    match2 = re.search(r"(\{activeTab === 'purchase' && \(\n\s*<div className=\"mt-4\">.*?)(?=\n      \)\}\n    </div>)", content, re.DOTALL)
    if match2:
        purchase_block = match2.group(1)
        with open('purchase_block.txt', 'w') as f:
            f.write(purchase_block)

main()
