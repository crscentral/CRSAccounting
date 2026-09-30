import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

if "getAmcActiveMonths" not in content:
    content = content.replace("import { getYTDRange } from '../lib/fiscalYear'", "import { getYTDRange, getAmcActiveMonths, getAmcMonthsInView } from '../lib/fiscalYear'")

overlap_helper = """
function getAmcOverlapUsd(r, fyStart, rangeFrom, rangeTo) {
  const activeMonths = getAmcActiveMonths(r.start_year, r.start_month, fyStart).totalMonths;
  const amount = Number(r.annual_amount_usd || 0);
  const monthlyAmount = activeMonths > 0 ? amount / activeMonths : 0;
  const overlapMonths = getAmcMonthsInView(r.start_year, r.start_month, fyStart, rangeFrom, rangeTo);
  return monthlyAmount * overlapMonths;
}
"""
if "getAmcOverlapUsd" not in content:
    content = content.replace("export default function Analytics() {", overlap_helper + "\nexport default function Analytics() {")

# Add prodFilter
content = content.replace("async function loadData() {\n", "async function loadData() {\n    const prodFilter = activeProduct === 'hotel' ? ['hotel', 'restaurant'] : [activeProduct]\n")

# Replace .eq('product', activeProduct) with .in('product', prodFilter) in Analytics.jsx
content = re.sub(r"\.eq\('product', activeProduct\)", ".in('product', prodFilter)", content)

# Replace amcTotal
content = re.sub(
    r"const amcTotal = \(hotelAmc \|\| \[\]\)\.reduce\(\(s, r\) => s \+ \(Number\(r\.annual_amount_usd\) / 12\), 0\) \* monthsInView",
    "const fyStart = activeCompany.fiscal_year_start_month || 1;\n    const amcTotal = (hotelAmc || []).reduce((s, r) => s + getAmcOverlapUsd(r, fyStart, cp.range.from, cp.range.to), 0)",
    content
)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)
