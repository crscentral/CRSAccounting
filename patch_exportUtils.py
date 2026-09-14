import re

with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

# 1. Phone number format
clean_phone_fn = """
function cleanPhone(p) {
  if (!p) return null;
  let s = p.replace(/[\\s.]+/g, '').trim();
  if (s.startsWith('+')) {
    s = s.replace(/^(\\+\\d{2,3})(\\d+)/, '$1 $2');
  }
  return s;
}
"""
code = code.replace("function sanitizeText(str) {", clean_phone_fn + "\nfunction sanitizeText(str) {")

contact_lines_repl = """  const companyLines = [
    company?.legal_name,
    company?.address,
    [company?.city, company?.country].filter(Boolean).join(', '),
    company?.email, cleanPhone(company?.phone), company?.website,
    company?.tax_id ? `Tax ID: ${company.tax_id}` : null,
  ].filter(Boolean)
  
  const contactLines = [
    invoice.customer_address || contact?.address || invoice.supplier_address,
    invoice.customer_email || contact?.email || invoice.supplier_email,
    cleanPhone(invoice.customer_phone || contact?.phone || invoice.supplier_phone),
    invoice.supplier_gstin ? `GSTIN: ${invoice.supplier_gstin}` : null,
  ].filter(Boolean)"""

code = re.sub(
    r"  const companyLines = \[\n    company\?\.legal_name,\n    company\?\.address,\n    \[company\?\.city, company\?\.country\]\.filter\(Boolean\)\.join\(', '\),\n    company\?\.email, company\?\.phone, company\?\.website,\n    company\?\.tax_id \? `Tax ID: \$\{company\.tax_id\}` : null,\n  \]\.filter\(Boolean\)\n  \n  const contactLines = \[\n    invoice\.customer_address \|\| contact\?\.address \|\| invoice\.supplier_address,\n    invoice\.customer_email \|\| contact\?\.email \|\| invoice\.supplier_email,\n    invoice\.customer_phone \|\| contact\?\.phone \|\| invoice\.supplier_phone,\n    invoice\.supplier_gstin \? `GSTIN: \$\{invoice\.supplier_gstin\}` : null,\n  \]\.filter\(Boolean\)",
    contact_lines_repl,
    code
)

# 2. Discount format
discount_repl = """    ...(isSales && invoice.discount_value ? [
      [
        `Discount ${invoice.discount_type === 'percent' ? `(${invoice.discount_value}%)` : '(fixed)'}`,
        `-${(invoice.discount_type === 'percent' ? ((invoice.subtotal ?? invoice.amount) * (invoice.discount_value / 100)) : invoice.discount_value).toFixed(2)}`
      ]
    ] : []),"""

code = re.sub(
    r"    \.\.\.\(isSales && invoice\.discount_value \? \[\[`Invoice discount \(\$\{invoice\.discount_type === 'percent' \? '%' : 'fixed'\}\)`, `-\$\{Number\(invoice\.discount_value\)\.toFixed\(2\)\}`\]\] : \[\]\),",
    discount_repl,
    code
)

# 3. Rich text notes
rich_text_fn = """
function renderRichText(doc, text, startX, startY, maxWidth) {
  if (!text) return startY;
  const lines = text.split('\\n');
  let y = startY;
  const lineHeight = 4.5;
  
  lines.forEach(line => {
    let x = startX;
    const trimmed = line.trim();
    let indent = 0;
    
    let isBullet = trimmed.match(/^[-*]\\s/);
    let isNum = trimmed.match(/^(\\d+\\.)\\s/);
    
    let remainder = line;
    if (isBullet) {
      doc.setFont(undefined, 'normal');
      doc.text('•', x, y);
      indent = 4;
      x += indent;
      remainder = trimmed.replace(/^[-*]\\s/, '');
    } else if (isNum) {
      doc.setFont(undefined, 'normal');
      doc.text(isNum[1], x, y);
      indent = 7;
      x += indent;
      remainder = trimmed.replace(/^(\\d+\\.)\\s/, '');
    }
    
    const segments = remainder.split(/(\\**.*?\\**)/g);
    
    segments.forEach(seg => {
      if (!seg) return;
      let isBold = false;
      let txt = seg;
      if (seg.startsWith('**') && seg.endsWith('**') && seg.length > 4) {
        isBold = true;
        txt = seg.slice(2, -2);
      }
      
      doc.setFont(undefined, isBold ? 'bold' : 'normal');
      
      const words = txt.split(' ');
      words.forEach((word, i) => {
        const isLastWord = i === words.length - 1;
        const wordToPrint = isLastWord ? word : word + ' ';
        const wordWidth = doc.getTextWidth(wordToPrint);
        
        if (x + wordWidth > startX + maxWidth && x > startX + indent) {
          y += lineHeight;
          x = startX + indent;
        }
        doc.text(wordToPrint, x, y);
        x += wordWidth;
      });
    });
    y += lineHeight;
  });
  return y;
}
"""
code = code.replace("function sanitizeText(str) {", rich_text_fn + "\nfunction sanitizeText(str) {")

notes_repl = """  if (invoice.payment_terms || invoice.notes) {
    const combined = [invoice.payment_terms, invoice.notes].filter(Boolean).join('\\n\\n')
    finalY = renderRichText(doc, combined, 14, finalY, pageWidth - 28)
  }"""

code = re.sub(
    r"  if \(invoice\.payment_terms \|\| invoice\.notes\) \{\n    const wrapped = doc\.splitTextToSize\(\[invoice\.payment_terms, invoice\.notes\]\.filter\(Boolean\)\.join\('  '\), pageWidth - 28\)\n    doc\.text\(wrapped, 14, finalY\)\n    finalY \+= wrapped\.length \* 4\n  \}",
    notes_repl,
    code
)


with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
