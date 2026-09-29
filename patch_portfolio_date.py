import re

def patch():
    with open('src/pages/PortfolioDashboard.jsx', 'r') as f:
        content = f.read()

    old_code = "const monthsInView = (range.to.substring(0,4) - range.from.substring(0,4)) * 12 + (range.to.substring(5,7) - range.from.substring(5,7)) + 1"
    new_code = """const start = new Date(range.from)
      const end = new Date(range.to)
      const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1"""

    if old_code in content:
        content = content.replace(old_code, new_code)
        with open('src/pages/PortfolioDashboard.jsx', 'w') as f:
            f.write(content)
        print("Patched PortfolioDashboard.jsx")
    else:
        print("Could not find old code block")

patch()
