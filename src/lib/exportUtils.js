import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import * as XLSX from 'xlsx'

/**
 * Exports tabular data (columns + rows of plain values) as a PDF.
 * title: page/report title. subtitle: e.g. company name + period.
 */
export function exportTableToPDF({ title, subtitle, columns, rows, filename }) {
  const doc = new jsPDF()
  doc.setFontSize(16)
  doc.setTextColor(27, 58, 107) // navy
  doc.text(title, 14, 18)
  if (subtitle) {
    doc.setFontSize(10)
    doc.setTextColor(100)
    doc.text(subtitle, 14, 25)
  }
  autoTable(doc, {
    startY: subtitle ? 32 : 26,
    head: [columns],
    body: rows,
    headStyles: { fillColor: [27, 58, 107] },
    styles: { fontSize: 9 },
  })
  doc.save(`${filename}.pdf`)
}

/** Exports tabular data as an .xlsx Excel file. */
export function exportTableToExcel({ title, columns, rows, filename }) {
  const wsData = [columns, ...rows]
  const ws = XLSX.utils.aoa_to_sheet(wsData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, title.slice(0, 31) || 'Report')
  XLSX.writeFile(wb, `${filename}.xlsx`)
}

/**
 * Exports tabular data as a Word-compatible file. True .docx generation needs a heavy
 * library; instead we generate valid HTML with a .doc extension, which Word (desktop,
 * Mac, and Word Online) opens natively and renders as a normal formatted document.
 */
export function exportTableToWord({ title, subtitle, columns, rows, filename }) {
  const headerCells = columns.map(c => `<th style="background:#1B3A6B;color:#fff;padding:6px 10px;text-align:left;">${escapeHtml(c)}</th>`).join('')
  const bodyRows = rows.map(r =>
    `<tr>${r.map(cell => `<td style="padding:6px 10px;border:1px solid #ddd;">${escapeHtml(String(cell ?? ''))}</td>`).join('')}</tr>`
  ).join('')

  const html = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset="utf-8"><title>${escapeHtml(title)}</title></head>
    <body style="font-family:Arial,sans-serif;">
      <h2 style="color:#1B3A6B;">${escapeHtml(title)}</h2>
      ${subtitle ? `<p style="color:#666;">${escapeHtml(subtitle)}</p>` : ''}
      <table style="border-collapse:collapse;width:100%;">
        <thead><tr>${headerCells}</tr></thead>
        <tbody>${bodyRows}</tbody>
      </table>
    </body>
    </html>
  `
  const blob = new Blob(['\ufeff', html], { type: 'application/msword' })
  downloadBlob(blob, `${filename}.doc`)
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]))
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// Falls back to the company's *current* LUT number/date whenever the invoice's own
// stored value is missing (e.g. an invoice saved before the company's LUT was set,
// or a stale cached company object at save-time). New invoices freeze the company's
// LUT value at creation as usual; this only fills the gap when that didn't happen.
function resolveLutInfo(invoice, company) {
  if (!invoice.is_export_lut) return { number: null, date: null }
  return {
    number: invoice.lut_ack_number || company?.lut_ack_number || null,
    date: invoice.lut_date || company?.lut_expiry_date || null,
  }
}

/** Loads a remote image URL and returns a base64 data URL + its natural aspect ratio, for embedding in jsPDF. */
function loadImageAsDataUrl(url) {
  return new Promise((resolve) => {
    if (!url) { resolve(null); return }
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        canvas.width = img.naturalWidth
        canvas.height = img.naturalHeight
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0)
        resolve({ dataUrl: canvas.toDataURL('image/png'), ratio: img.naturalWidth / img.naturalHeight })
      } catch {
        resolve(null) // CORS-blocked or failed to load -- fall back to no logo rather than break the PDF
      }
    }
    img.onerror = () => resolve(null)
    img.src = url
  })
}

/**
 * Generates a single formatted invoice PDF (sales or purchase), laid out to match
 * the original CRS Central invoice template: TAX INVOICE header, three-column
 * FROM / BILL TO / DOCUMENT block, two-line item descriptions, full summary
 * (Subtotal/Discount/Tax/Grand Total/Paid/Balance Due), LUT acknowledgement line,
 * payment terms, bank details, and a centered legal-name footer.
 */
export async function exportInvoicePDF({ type, invoice, items, company, contact, itemDescription }) {
  const doc = new jsPDF()
  const isSales = type === 'sales'
  const pageWidth = doc.internal.pageSize.getWidth()
  const rightX = pageWidth - 14

  const logo = await loadImageAsDataUrl(company?.logo_url)

  // Header: title + status badge, logo top-right (bigger, per request)
  doc.setFontSize(24)
  doc.setTextColor(20)
  doc.setFont(undefined, 'bold')
  doc.text('Invoice', 14, 22)

  const status = invoice.status || 'Draft'
  const statusColors = {
    Paid: [16, 150, 100], Draft: [148, 163, 184], Overdue: [220, 38, 38], Cancelled: [148, 163, 184],
  }
  const [r, g, b] = statusColors[status] || statusColors.Draft
  doc.setFillColor(r, g, b)
  doc.setFontSize(9)
  doc.setFont(undefined, 'normal')
  const badgeWidth = doc.getTextWidth(status) + 8
  doc.roundedRect(14, 26, badgeWidth, 7, 1.5, 1.5, 'F')
  doc.setTextColor(255)
  doc.text(status, 18, 30.8)

  if (logo?.dataUrl) {
    const logoH = 16 // bigger logo, per request
    const logoW = logoH * logo.ratio
    doc.addImage(logo.dataUrl, 'PNG', rightX - logoW, 10, logoW, logoH)
  }

  let y = 42
  doc.setFontSize(9)
  doc.setTextColor(90)
  doc.setFont(undefined, 'bold')
  doc.text('TAX INVOICE', pageWidth / 2, y, { align: 'center' })
  y += 5
  doc.setFont(undefined, 'normal')
  doc.setFontSize(8)
  if (isSales && invoice.is_export_lut) {
    doc.text('(Supply meant for export under LUT without payment of Integrated Tax)', pageWidth / 2, y, { align: 'center' })
    y += 5
  }
  doc.setDrawColor(220)
  doc.line(14, y, rightX, y)
  y += 8

  // FROM / BILL TO / DOCUMENT three-column block
  const col1 = 14, col2 = 80, col3 = 150
  doc.setFontSize(8)
  doc.setTextColor(150)
  doc.text('FROM', col1, y)
  doc.text(isSales ? 'BILL TO' : 'SUPPLIER', col2, y)
  doc.text('DOCUMENT', col3, y)
  y += 5.5

  doc.setFontSize(10)
  doc.setFont(undefined, 'bold')
  doc.setTextColor(20)
  doc.text(company?.name || '', col1, y)
  doc.text(contact?.name || invoice.supplier_name_freeform || '', col2, y)
  doc.text(invoice.invoice_number || '', col3, y)
  y += 4.5

  doc.setFont(undefined, 'normal')
  doc.setFontSize(8)
  doc.setTextColor(90)
  const fromLines = [
    company?.legal_name,
    company?.address,
    [company?.city, company?.country].filter(Boolean).join(', '),
    company?.email, company?.phone, company?.website,
    company?.tax_id ? `Tax ID: ${company.tax_id}` : null,
  ].filter(Boolean)
  const billLines = [
    invoice.customer_address || contact?.address || invoice.supplier_address,
    invoice.customer_email || contact?.email || invoice.supplier_email,
    invoice.customer_phone || contact?.phone || invoice.supplier_phone,
    invoice.supplier_gstin ? `GSTIN: ${invoice.supplier_gstin}` : null,
  ].filter(Boolean)
  const docLines = [
    `Issue: ${invoice.invoice_date}`,
    `Due: ${invoice.due_date || '—'}`,
    isSales ? `Terms: ${invoice.billing_terms || '—'}` : null,
    `Currency: ${invoice.currency}`,
  ].filter(Boolean)
  // Render each column independently with its own running Y position, so a wrapped
  // multi-line address in one column never overlaps the next field in that same
  // column (previous bug: fixed line-height advance regardless of wrap count).
  function renderColumn(lines, x, maxWidth, startY) {
    let cy = startY
    lines.forEach(line => {
      const wrapped = doc.splitTextToSize(line, maxWidth)
      doc.text(wrapped, x, cy)
      cy += wrapped.length * 4.5
    })
    return cy
  }
  const colStartY = y
  const endY1 = renderColumn(fromLines, col1, 60, colStartY)
  const endY2 = renderColumn(billLines, col2, 62, colStartY)
  const endY3 = renderColumn(docLines, col3, 55, colStartY)
  y = Math.max(endY1, endY2, endY3) + 6

  // Line items -- two-line description like the original (bold name + gray subtitle)
  const tableColumns = isSales
    ? ['Item', 'Qty', 'Price', 'Tax %', 'Total']
    : ['Product', 'HSN/SAC', 'Qty', 'Unit Price', 'Tax %', 'Total']
  const tableRows = (items || []).map(it => {
    const mainLabel = isSales ? (it.description || '') : (it.product_name || '')
    const subtitle = isSales && itemDescription ? itemDescription : null
    const label = subtitle ? `${mainLabel}\n${subtitle}` : mainLabel
    return isSales
      ? [label, it.qty, Number(it.unit_price).toFixed(2), `${it.tax_percent}%`, Number(it.line_total).toFixed(2)]
      : [label, it.hsn_sac || '—', it.qty, Number(it.unit_price).toFixed(2), `${it.tax_percent}%`, Number(it.line_total).toFixed(2)]
  })

  autoTable(doc, {
    startY: y,
    head: [tableColumns],
    body: tableRows,
    headStyles: { fillColor: [27, 58, 107], fontSize: 9 },
    styles: { fontSize: 9, cellPadding: 3 },
    columnStyles: isSales ? { 0: { cellWidth: 90 } } : { 0: { cellWidth: 70 } },
    didParseCell: (data) => {
      if (data.column.index === 0 && data.cell.raw && String(data.cell.raw).includes('\n')) {
        data.cell.styles.fontStyle = 'normal'
      }
    },
  })

  let finalY = doc.lastAutoTable.finalY + 8
  const grandTotal = Number(isSales ? invoice.amount : (invoice.net_payable ?? invoice.amount))
  const paid = Number(invoice.paid_amount || 0)
  const summaryRows = [
    ['Subtotal', (invoice.subtotal ?? invoice.amount)?.toFixed(2)],
    ...(isSales && invoice.discount_value ? [[`Invoice discount (${invoice.discount_type === 'percent' ? '%' : 'fixed'})`, `-${Number(invoice.discount_value).toFixed(2)}`]] : []),
    ['Tax', Number(invoice.tax_amount ?? 0).toFixed(2)],
    ...(isSales && invoice.bank_charges ? [['Bank Charges', Number(invoice.bank_charges).toFixed(2)]] : []),
    ...(!isSales && invoice.tds_percent ? [[`TDS (${invoice.tds_percent}%)`, `-${(((invoice.subtotal || 0) + (invoice.tax_amount || 0)) * invoice.tds_percent / 100).toFixed(2)}`]] : []),
  ]
  doc.setFontSize(9)
  summaryRows.forEach(([label, val]) => {
    doc.setFont(undefined, 'normal')
    doc.setTextColor(90)
    doc.text(label, 130, finalY)
    doc.setTextColor(20)
    doc.text(`${val} ${invoice.currency}`, rightX, finalY, { align: 'right' })
    finalY += 6
  })

  doc.setDrawColor(220)
  doc.line(130, finalY - 2, rightX, finalY - 2)
  doc.setFont(undefined, 'bold')
  doc.setFontSize(11)
  doc.text(isSales ? 'Grand total' : 'Net Payable', 130, finalY + 3)
  doc.text(`${grandTotal.toFixed(2)} ${invoice.currency}`, rightX, finalY + 3, { align: 'right' })
  finalY += 9

  if (isSales) {
    doc.setFont(undefined, 'normal')
    doc.setFontSize(9)
    doc.setTextColor(90)
    doc.text('Paid', 130, finalY)
    doc.setTextColor(20)
    doc.text(`${paid.toFixed(2)} ${invoice.currency}`, rightX, finalY, { align: 'right' })
    finalY += 6
    doc.setFont(undefined, 'bold')
    doc.setTextColor(20)
    doc.text('Balance due', 130, finalY)
    doc.text(`${Math.max(0, grandTotal - paid).toFixed(2)} ${invoice.currency}`, rightX, finalY, { align: 'right' })
    finalY += 6
  }

  finalY += 6
  doc.setFontSize(8)
  doc.setFont(undefined, 'normal')
  doc.setTextColor(90)
  const lutInfo = resolveLutInfo(invoice, company)
  if (isSales && lutInfo.number) {
    doc.text(`The LUT acknowledgement number is ${lutInfo.number}${lutInfo.date ? ` dated ${lutInfo.date}` : ''}`, 14, finalY)
    finalY += 6
  }

  if (invoice.payment_terms || invoice.notes) {
    const wrapped = doc.splitTextToSize([invoice.payment_terms, invoice.notes].filter(Boolean).join('  '), pageWidth - 28)
    doc.text(wrapped, 14, finalY)
    finalY += wrapped.length * 4
  }

  if (isSales && company?.bank_account_number) {
    finalY += 6
    doc.setDrawColor(220)
    doc.line(14, finalY - 4, rightX, finalY - 4)
    doc.setFontSize(8)
    doc.setTextColor(150)
    doc.text('BANK DETAILS', 14, finalY)
    finalY += 5
    doc.setTextColor(60)
    const bankLines = [
      `Bank: ${company.bank_name || ''}`,
      `Account Holder: ${company.bank_account_holder || ''}`,
      `Account Number: ${company.bank_account_number || ''}`,
      `Branch: ${company.bank_branch || ''}`,
      `SWIFT Code: ${company.bank_swift_code || ''}`,
    ]
    bankLines.forEach(line => { doc.text(line, 14, finalY); finalY += 4.5 })
  }

  finalY += 10
  doc.setDrawColor(230)
  doc.line(14, finalY - 5, rightX, finalY - 5)
  doc.setFontSize(9)
  doc.setTextColor(150)
  doc.text(company?.legal_name || company?.name || '', pageWidth / 2, finalY, { align: 'center' })

  if (invoice.thank_you_note) {
    doc.setFontSize(8)
    doc.setTextColor(180)
    doc.text(invoice.thank_you_note, pageWidth / 2, finalY + 6, { align: 'center' })
  }

  doc.save(`${invoice.invoice_number}.pdf`)
}

/** Exports a single invoice as a formatted Excel workbook (header info + line items + summary). */
export function exportInvoiceExcel({ type, invoice, items, company, contact }) {
  const isSales = type === 'sales'
  const rows = []
  rows.push(['INVOICE', invoice.invoice_number, '', 'Status:', invoice.status || 'Draft'])
  rows.push([])
  rows.push(['From', company?.name || '', '', isSales ? 'Bill To' : 'Supplier', contact?.name || invoice.supplier_name_freeform || ''])
  rows.push(['', company?.address || '', '', '', invoice.customer_address || invoice.supplier_address || ''])
  rows.push(['', company?.email || '', '', '', invoice.customer_email || invoice.supplier_email || ''])
  rows.push([])
  rows.push(['Issue Date', invoice.invoice_date, '', 'Due Date', invoice.due_date || ''])
  rows.push(['Currency', invoice.currency, '', isSales ? 'Terms' : 'GSTIN', isSales ? (invoice.billing_terms || '') : (invoice.supplier_gstin || '')])
  rows.push([])
  rows.push(isSales ? ['Item', 'Qty', 'Price', 'Tax %', 'Total'] : ['Product', 'HSN/SAC', 'Qty', 'Unit Price', 'Tax %', 'Total'])
  ;(items || []).forEach(it => {
    rows.push(isSales
      ? [it.description, it.qty, it.unit_price, `${it.tax_percent}%`, it.line_total]
      : [it.product_name, it.hsn_sac || '', it.qty, it.unit_price, `${it.tax_percent}%`, it.line_total])
  })
  rows.push([])
  rows.push(['', '', '', 'Subtotal', invoice.subtotal ?? invoice.amount])
  if (isSales && invoice.discount_value) rows.push(['', '', '', 'Discount', -invoice.discount_value])
  rows.push(['', '', '', 'Tax', invoice.tax_amount ?? 0])
  if (isSales && invoice.bank_charges) rows.push(['', '', '', 'Bank Charges', invoice.bank_charges])
  if (!isSales && invoice.tds_percent) rows.push(['', '', '', `TDS (${invoice.tds_percent}%)`, -(((invoice.subtotal || 0) + (invoice.tax_amount || 0)) * invoice.tds_percent / 100)])
  rows.push(['', '', '', isSales ? 'Grand Total' : 'Net Payable', isSales ? invoice.amount : (invoice.net_payable ?? invoice.amount)])
  if (isSales) {
    rows.push(['', '', '', 'Paid', invoice.paid_amount || 0])
    rows.push(['', '', '', 'Balance Due', Math.max(0, invoice.amount - (invoice.paid_amount || 0))])
  }
  const lutInfoXl = resolveLutInfo(invoice, company)
  if (isSales && lutInfoXl.number) {
    rows.push([])
    rows.push(['LUT Acknowledgement Number', lutInfoXl.number, '', 'LUT Date', lutInfoXl.date || ''])
  }
  if (isSales && company?.bank_account_number) {
    rows.push([])
    rows.push(['Bank Details'])
    rows.push(['Bank', company.bank_name || ''])
    rows.push(['Account Holder', company.bank_account_holder || ''])
    rows.push(['Account Number', company.bank_account_number || ''])
    rows.push(['Branch', company.bank_branch || ''])
    rows.push(['SWIFT', company.bank_swift_code || ''])
  }

  const ws = XLSX.utils.aoa_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, invoice.invoice_number.slice(0, 31))
  XLSX.writeFile(wb, `${invoice.invoice_number}.xlsx`)
}

/** Exports a single invoice as a Word-compatible (.doc) file matching the same layout. */
export function exportInvoiceWord({ type, invoice, items, company, contact }) {
  const isSales = type === 'sales'
  const esc = (s) => escapeHtml(String(s ?? ''))
  const itemRows = (items || []).map(it => isSales
    ? `<tr><td style="padding:6px;border:1px solid #ddd;">${esc(it.description)}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.qty)}</td><td style="padding:6px;border:1px solid #ddd;">${esc(Number(it.unit_price).toFixed(2))}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.tax_percent)}%</td><td style="padding:6px;border:1px solid #ddd;">${esc(Number(it.line_total).toFixed(2))}</td></tr>`
    : `<tr><td style="padding:6px;border:1px solid #ddd;">${esc(it.product_name)}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.hsn_sac || '')}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.qty)}</td><td style="padding:6px;border:1px solid #ddd;">${esc(Number(it.unit_price).toFixed(2))}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.tax_percent)}%</td><td style="padding:6px;border:1px solid #ddd;">${esc(Number(it.line_total).toFixed(2))}</td></tr>`
  ).join('')
  const headerCells = (isSales ? ['Item', 'Qty', 'Price', 'Tax %', 'Total'] : ['Product', 'HSN/SAC', 'Qty', 'Unit Price', 'Tax %', 'Total'])
    .map(c => `<th style="background:#1B3A6B;color:#fff;padding:6px;text-align:left;">${esc(c)}</th>`).join('')

  const grandTotal = Number(isSales ? invoice.amount : (invoice.net_payable ?? invoice.amount))
  const bankHtml = isSales && company?.bank_account_number ? `
    <p style="color:#999;font-size:11px;margin-top:20px;">BANK DETAILS</p>
    <p>Bank: ${esc(company.bank_name)}<br/>Account Holder: ${esc(company.bank_account_holder)}<br/>Account Number: ${esc(company.bank_account_number)}<br/>Branch: ${esc(company.bank_branch)}<br/>SWIFT: ${esc(company.bank_swift_code)}</p>
  ` : ''

  const html = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset="utf-8"><title>${esc(invoice.invoice_number)}</title></head>
    <body style="font-family:Arial,sans-serif;color:#333;">
      <h1 style="margin-bottom:0;">Invoice</h1>
      <p style="color:#666;text-transform:uppercase;font-size:12px;">${esc(invoice.status || 'Draft')}</p>
      <table style="width:100%;margin-bottom:16px;"><tr>
        <td style="vertical-align:top;width:33%;">
          <p style="color:#999;font-size:11px;">FROM</p>
          <p><strong>${esc(company?.name)}</strong><br/>${esc(company?.legal_name)}<br/>${esc(company?.address)}<br/>${esc(company?.email)}<br/>${company?.tax_id ? 'Tax ID: ' + esc(company.tax_id) : ''}</p>
        </td>
        <td style="vertical-align:top;width:33%;">
          <p style="color:#999;font-size:11px;">${isSales ? 'BILL TO' : 'SUPPLIER'}</p>
          <p><strong>${esc(contact?.name || invoice.supplier_name_freeform)}</strong><br/>${esc(invoice.customer_address || invoice.supplier_address)}<br/>${esc(invoice.customer_email || invoice.supplier_email)}</p>
        </td>
        <td style="vertical-align:top;width:33%;">
          <p style="color:#999;font-size:11px;">DOCUMENT</p>
          <p><strong>${esc(invoice.invoice_number)}</strong><br/>Issue: ${esc(invoice.invoice_date)}<br/>Due: ${esc(invoice.due_date || '—')}<br/>Currency: ${esc(invoice.currency)}</p>
        </td>
      </tr></table>
      <table style="border-collapse:collapse;width:100%;"><thead><tr>${headerCells}</tr></thead><tbody>${itemRows}</tbody></table>
      <table style="width:100%;margin-top:12px;"><tr><td style="width:70%;"></td><td>
        <p>Subtotal: ${esc((invoice.subtotal ?? invoice.amount)?.toFixed(2))} ${esc(invoice.currency)}</p>
        ${isSales && invoice.discount_value ? `<p>Discount: -${esc(Number(invoice.discount_value).toFixed(2))} ${esc(invoice.currency)}</p>` : ''}
        <p>Tax: ${esc(Number(invoice.tax_amount ?? 0).toFixed(2))} ${esc(invoice.currency)}</p>
        <p><strong>${isSales ? 'Grand Total' : 'Net Payable'}: ${esc(grandTotal.toFixed(2))} ${esc(invoice.currency)}</strong></p>
        ${isSales ? `<p>Paid: ${esc(Number(invoice.paid_amount || 0).toFixed(2))} ${esc(invoice.currency)}</p><p><strong>Balance Due: ${esc(Math.max(0, grandTotal - (invoice.paid_amount || 0)).toFixed(2))} ${esc(invoice.currency)}</strong></p>` : ''}
      </td></tr></table>
      ${(() => { const l = resolveLutInfo(invoice, company); return isSales && l.number ? `<p style="font-size:11px;color:#666;">The LUT acknowledgement number is ${esc(l.number)}${l.date ? ' dated ' + esc(l.date) : ''}</p>` : '' })()}
      <p style="font-size:11px;color:#666;">${esc(invoice.payment_terms || '')} ${esc(invoice.notes || '')}</p>
      ${bankHtml}
      <p style="text-align:center;color:#999;margin-top:24px;">${esc(company?.legal_name || company?.name)}</p>
    </body>
    </html>
  `
  const blob = new Blob(['\ufeff', html], { type: 'application/msword' })
  downloadBlob(blob, `${invoice.invoice_number}.doc`)
}

/**
 * Multi-section report export -- used by the "choose what to include" Download Report
 * flow on every page (Dashboard, Chart of Accounts, Analytics, etc). Each section is
 * either a data table ({ heading, columns, rows }) or a set of summary key/value pairs
 * ({ heading, keyValuePairs: [[label, value], ...] }).
 */
export function exportMultiSectionPDF({ title, subtitle, sections, filename }) {
  const doc = new jsPDF()
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()

  doc.setFontSize(16)
  doc.setTextColor(27, 58, 107)
  doc.text(title, 14, 18)
  if (subtitle) {
    doc.setFontSize(10)
    doc.setTextColor(100)
    doc.text(subtitle, 14, 25)
  }

  let y = subtitle ? 33 : 27

  sections.forEach(section => {
    if (y > pageHeight - 30) { doc.addPage(); y = 20 }

    doc.setFontSize(12)
    doc.setTextColor(20)
    doc.setFont(undefined, 'bold')
    doc.text(section.heading, 14, y)
    y += 3
    doc.setFont(undefined, 'normal')

    if (section.keyValuePairs) {
      y += 4
      doc.setFontSize(9)
      section.keyValuePairs.forEach(([label, val]) => {
        if (y > pageHeight - 15) { doc.addPage(); y = 20 }
        doc.setTextColor(90)
        doc.text(String(label), 16, y)
        doc.setTextColor(20)
        doc.text(String(val), 100, y)
        y += 5.5
      })
      y += 6
    } else if (section.columns && section.rows) {
      autoTable(doc, {
        startY: y + 3,
        head: [section.columns],
        body: section.rows,
        headStyles: { fillColor: [27, 58, 107], fontSize: 8 },
        styles: { fontSize: 8, cellPadding: 2.5 },
        margin: { left: 14, right: 14 },
      })
      y = doc.lastAutoTable.finalY + 10
    }
  })

  doc.save(`${filename}.pdf`)
}

/** Multi-section Excel export -- one section per block, stacked in a single sheet with spacing rows. */
export function exportMultiSectionExcel({ title, sections, filename }) {
  const rows = [[title], []]
  sections.forEach(section => {
    rows.push([section.heading])
    if (section.keyValuePairs) {
      section.keyValuePairs.forEach(([label, val]) => rows.push([label, val]))
    } else if (section.columns && section.rows) {
      rows.push(section.columns)
      section.rows.forEach(r => rows.push(r))
    }
    rows.push([])
  })
  const ws = XLSX.utils.aoa_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, title.slice(0, 31) || 'Report')
  XLSX.writeFile(wb, `${filename}.xlsx`)
}

/** Multi-section Word export. */
export function exportMultiSectionWord({ title, subtitle, sections, filename }) {
  const esc = escapeHtml
  const sectionsHtml = sections.map(section => {
    let inner = ''
    if (section.keyValuePairs) {
      inner = section.keyValuePairs.map(([label, val]) =>
        `<p style="margin:2px 0;"><strong>${esc(label)}:</strong> ${esc(val)}</p>`
      ).join('')
    } else if (section.columns && section.rows) {
      const head = section.columns.map(c => `<th style="background:#1B3A6B;color:#fff;padding:5px 8px;text-align:left;">${esc(c)}</th>`).join('')
      const body = section.rows.map(r =>
        `<tr>${r.map(cell => `<td style="padding:5px 8px;border:1px solid #ddd;">${esc(cell)}</td>`).join('')}</tr>`
      ).join('')
      inner = `<table style="border-collapse:collapse;width:100%;margin-bottom:12px;"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`
    }
    return `<h3 style="color:#1B3A6B;margin-top:20px;">${esc(section.heading)}</h3>${inner}`
  }).join('')

  const html = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset="utf-8"><title>${esc(title)}</title></head>
    <body style="font-family:Arial,sans-serif;">
      <h1 style="color:#1B3A6B;margin-bottom:0;">${esc(title)}</h1>
      ${subtitle ? `<p style="color:#666;">${esc(subtitle)}</p>` : ''}
      ${sectionsHtml}
    </body>
    </html>
  `
  const blob = new Blob(['\ufeff', html], { type: 'application/msword' })
  downloadBlob(blob, `${filename}.doc`)
}
