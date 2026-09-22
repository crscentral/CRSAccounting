import re

with open('src/lib/exportUtils.js', 'r') as f:
    content = f.read()

# 1. Remove cleanPhone properly
old_clean = """function cleanPhone(p) {
  if (!p) return null;
  let s = p.replace(/[\s.]+/g, '').trim();
  if (s.startsWith('+')) {
    s = s.replace(/^(\+\d{2,3})(\d+)/, '$1 $2');
  }
  return s;
}"""
content = content.replace(old_clean, '')

# 2. Remove cleanPhone usage
content = content.replace('cleanPhone(company?.phone)', 'company?.phone')
content = content.replace('cleanPhone(invoice.customer_phone || contact?.phone || invoice.supplier_phone)', 'invoice.customer_phone || contact?.phone || invoice.supplier_phone')

# 3. Add trim() to address lines
old_contact_lines = """  const contactLines = [
    invoice.customer_address || contact?.address || invoice.supplier_address,
    invoice.customer_email || contact?.email || invoice.supplier_email,
    invoice.customer_phone || contact?.phone || invoice.supplier_phone,
    invoice.supplier_gstin ? `GSTIN: ${invoice.supplier_gstin}` : null,
  ].filter(Boolean)"""

new_contact_lines = """  const contactLines = [
    (invoice.customer_address || contact?.address || invoice.supplier_address || '').trim(),
    (invoice.customer_email || contact?.email || invoice.supplier_email || '').trim(),
    (invoice.customer_phone || contact?.phone || invoice.supplier_phone || '').trim(),
    invoice.supplier_gstin ? `GSTIN: ${invoice.supplier_gstin}` : null,
  ].filter(Boolean)"""
content = content.replace(old_contact_lines, new_contact_lines)

old_company_lines = """  const companyLines = [
    company?.legal_name,
    company?.address,
    [company?.city, company?.country].filter(Boolean).join(', '),
    company?.email, company?.phone, company?.website,
    company?.tax_id ? `Tax ID: ${company.tax_id}` : null,
  ].filter(Boolean)"""

new_company_lines = """  const companyLines = [
    (company?.legal_name || '').trim(),
    (company?.address || '').trim(),
    [company?.city, company?.country].filter(Boolean).join(', ').trim(),
    (company?.email || '').trim(), 
    (company?.phone || '').trim(), 
    (company?.website || '').trim(),
    company?.tax_id ? `Tax ID: ${company.tax_id}` : null,
  ].filter(Boolean)"""
content = content.replace(old_company_lines, new_company_lines)

old_render = """  function renderColumn(lines, x, maxWidth, startY) {
    let cy = startY
    lines.forEach(line => {
      const wrapped = doc.splitTextToSize(line, maxWidth)
      doc.text(wrapped, x, cy)
      cy += wrapped.length * 4.5
    })
    return cy
  }"""

new_render = """  function renderColumn(lines, x, maxWidth, startY) {
    let cy = startY
    lines.forEach(line => {
      const explicitLines = line.split('\\n')
      explicitLines.forEach(el => {
        const wrapped = doc.splitTextToSize(el, maxWidth)
        wrapped.forEach(wl => {
          doc.text(wl, x, cy)
          cy += 4.5
        })
      })
    })
    return cy
  }"""
content = content.replace(old_render, new_render)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(content)
