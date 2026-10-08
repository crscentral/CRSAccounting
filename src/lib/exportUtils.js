import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import * as XLSX from 'xlsx'





function renderRichText(doc, text, startX, startY, maxWidth) {
  if (!text) return startY;
  const lines = text.split('\n');
  let y = startY;
  const lineHeight = 4.5;
  
  lines.forEach(line => {
    let x = startX;
    const trimmed = line.trim();
    let indent = 0;
    
    let isBullet = trimmed.match(/^[-*]\s/);
    let isNum = trimmed.match(/^(\d+\.)\s/);
    
    let remainder = line;
    if (isBullet) {
      doc.setFont(undefined, 'normal');
      doc.text('•', x, y);
      indent = 4;
      x += indent;
      remainder = trimmed.replace(/^[-*]\s/, '');
    } else if (isNum) {
      doc.setFont(undefined, 'normal');
      doc.text(isNum[1], x, y);
      indent = 7;
      x += indent;
      remainder = trimmed.replace(/^(\d+\.)\s/, '');
    }
    
    const segments = remainder.split(/(\*\*.*?\*\*)/g);
    
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

function sanitizeText(str) {
  if (typeof str !== 'string') return str;
  return str.replace(/₹/g, 'INR ').replace(/฿/g, 'THB ').replace(/€/g, 'EUR ').replace(/£/g, 'GBP ').replace(/[^\x00-\x7F]/g, '');
}


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
  const pageCount = doc.internal.getNumberOfPages()
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i)
    if (loadedLogo?.dataUrl) {
      const logoH = 12
      const logoW = logoH * loadedLogo.ratio
      doc.addImage(loadedLogo.dataUrl, 'PNG', pageWidth - 14 - logoW, 10, logoW, logoH)
    }
  }

  if (preview) {
    const blob = doc.output('blob')
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } else {
    doc.save(`${filename}.pdf`)
  }
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
export async function exportInvoicePDF({ type, invoice, items, company, contact, itemDescription, preview = false }) {
  const doc = new jsPDF()
  const isSales = type === 'sales'
  const isReceipt = type === 'receipt'
  const pageWidth = doc.internal.pageSize.getWidth()
  const rightX = pageWidth - 14

  const logo = await loadImageAsDataUrl(company?.logo_url)

  // Header: title + status badge, logo top-right (bigger, per request)
  doc.setFontSize(24)
  doc.setTextColor(20)
  doc.setFont(undefined, 'bold')
  const isProforma = isSales && invoice.invoice_type === 'proforma'
  let docHeading = 'Invoice'
  if (isProforma) docHeading = 'Proforma Invoice'
  if (!isSales && !isReceipt) docHeading = 'Purchase Invoice'
  if (isReceipt) docHeading = 'Payment Receipt'
  doc.text(docHeading, 14, 22)

  const status = isReceipt ? 'Received' : (invoice.status || 'Draft')
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
  doc.text(isReceipt ? 'PAYMENT RECEIPT' : isSales ? (isProforma ? 'PROFORMA INVOICE' : 'TAX INVOICE') : 'PURCHASE INVOICE', pageWidth / 2, y, { align: 'center' })
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
  doc.text('TO', col2, y)
  doc.text('DOCUMENT', col3, y)
  y += 5.5

  doc.setFontSize(10)
  doc.setFont(undefined, 'bold')
  doc.setTextColor(20)
  
  const fromName = (isSales || isReceipt) ? (company?.name || '') : (contact?.name || invoice.supplier_name_freeform || '')
  const toName = (isSales || isReceipt) ? (contact?.name || invoice.customer_name_freeform || invoice.customer_name || '') : (company?.name || '')
  
  const fromNameWrapped = doc.splitTextToSize(fromName, 60)
  const toNameWrapped = doc.splitTextToSize(toName, 62)
  const docNameWrapped = doc.splitTextToSize((isReceipt ? invoice.receipt_number : invoice.invoice_number) || '', 46)

  doc.text(fromNameWrapped, col1, y)
  doc.text(toNameWrapped, col2, y)
  doc.text(docNameWrapped, col3, y)
  
  const y1 = y + fromNameWrapped.length * 4.5
  const y2 = y + toNameWrapped.length * 4.5
  const y3 = y + docNameWrapped.length * 4.5

  doc.setFont(undefined, 'normal')
  doc.setFontSize(8)
  doc.setTextColor(90)
  
  const companyLines = [
    (company?.legal_name || '').trim(),
    (company?.address || '').trim(),
    [company?.city, company?.country].filter(Boolean).join(', ').trim(),
    (company?.email || '').trim(), 
    (company?.phone || '').trim(), 
    (company?.website || '').trim(),
    company?.tax_id ? `Tax ID: ${company.tax_id}` : null,
  ].filter(Boolean)
  
  const contactLines = [
    (invoice.customer_address || contact?.address || invoice.supplier_address || '').trim(),
    (invoice.customer_email || contact?.email || invoice.supplier_email || '').trim(),
    (invoice.customer_phone || contact?.phone || invoice.supplier_phone || '').trim(),
    invoice.supplier_gstin ? `GSTIN: ${invoice.supplier_gstin}` : null,
  ].filter(Boolean)
  
  const fromLines = isSales ? companyLines : contactLines
  const billLines = isSales ? contactLines : companyLines
  
  const docLines = [
    `Issue: ${invoice.invoice_date}`,
    `Due: ${invoice.due_date || '—'}`,
    `Terms: ${invoice.billing_terms || invoice.payment_terms || '—'}`,
    `Currency: ${invoice.currency}`,
    !isSales && invoice.expense_account_name ? `Expense Account: ${invoice.expense_account_name}` : null,
  ].filter(Boolean)
  // Render each column independently with its own running Y position, so a wrapped
  // multi-line address in one column never overlaps the next field in that same
  // column (previous bug: fixed line-height advance regardless of wrap count).
  function renderColumn(lines, x, maxWidth, startY) {
    let cy = startY
    lines.forEach(line => {
      const explicitLines = line.split('\n')
      explicitLines.forEach(el => {
        const wrapped = doc.splitTextToSize(el, maxWidth)
        wrapped.forEach(wl => {
          doc.text(wl, x, cy)
          cy += 4.5
        })
      })
    })
    return cy
  }
  const endY1 = renderColumn(fromLines, col1, 60, y1)
  const endY2 = renderColumn(billLines, col2, 62, y2)
  const endY3 = renderColumn(docLines, col3, 46, y3)
  y = Math.max(endY1, endY2, endY3) + 6

  // Line items -- two-line description like the original (bold name + gray subtitle)
  const tableColumns = isReceipt 
    ? ['Description', 'Amount']
    : isSales
      ? ['Item', 'Qty', 'Price', 'Tax %', 'Total']
      : ['Product', 'HSN/SAC', 'Qty', 'Unit Price', 'Tax %', 'Total']
  const tableRows = (items || []).map(it => {
    if (isReceipt) {
      return [it.description || 'Payment Received', Number(it.amount || invoice.amount).toFixed(2)]
    }
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
    ...(isSales && invoice.discount_value ? [
      [
        `Discount ${invoice.discount_type === 'percent' ? `(${invoice.discount_value}%)` : '(fixed)'}`,
        `-${(invoice.discount_type === 'percent' ? ((invoice.subtotal ?? invoice.amount) * (invoice.discount_value / 100)) : invoice.discount_value).toFixed(2)}`
      ]
    ] : []),
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

  const fxRate = Number(invoice.fx_rate_locked) || (invoice.amount ? (Number(invoice.amount) / Number(invoice.amount_usd)) : 1)
  const usdGrandTotal = Number(invoice.amount_usd) || grandTotal / (fxRate || 1)
  const usdPaid = paid / (fxRate || 1)
  const usdBalance = Math.max(0, grandTotal - paid) / (fxRate || 1)
  const printUsd = invoice.currency && invoice.currency !== 'USD'

  doc.setDrawColor(220)
  doc.line(130, finalY - 2, rightX, finalY - 2)
  doc.setFont(undefined, 'bold')
  doc.setFontSize(11)
  doc.text(isSales ? 'Grand total' : 'Net Payable', 130, finalY + 3)
  
  let grandTotalText = `${grandTotal.toFixed(2)} ${invoice.currency}`
  if (printUsd) grandTotalText += `  (USD ${usdGrandTotal.toFixed(2)})`
  doc.text(grandTotalText, rightX, finalY + 3, { align: 'right' })
  finalY += 9

  if (isSales) {
    doc.setFont(undefined, 'normal')
    doc.setFontSize(9)
    doc.setTextColor(90)
    doc.text('Paid', 130, finalY)
    doc.setTextColor(20)
    
    let paidText = `${paid.toFixed(2)} ${invoice.currency}`
    if (printUsd) paidText += `  (USD ${usdPaid.toFixed(2)})`
    doc.text(paidText, rightX, finalY, { align: 'right' })
    finalY += 6
    
    doc.setFont(undefined, 'bold')
    doc.setTextColor(20)
    doc.text('Balance due', 130, finalY)
    
    let balText = `${Math.max(0, grandTotal - paid).toFixed(2)} ${invoice.currency}`
    if (printUsd) balText += `  (USD ${usdBalance.toFixed(2)})`
    doc.text(balText, rightX, finalY, { align: 'right' })
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
    const combined = [invoice.payment_terms, invoice.notes].filter(Boolean).join("\n\n")
    finalY = renderRichText(doc, combined, 14, finalY, pageWidth - 28)
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

  if (preview) {
    const blob = doc.output('blob')
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } else {
    doc.save(`${invoice.invoice_number}.pdf`)
  }
}

/** Exports a single invoice as a formatted Excel workbook (header info + line items + summary). */
export function exportInvoiceExcel({ type, invoice, items, company, contact }) {
  const isSales = type === 'sales'
  const isReceipt = type === 'receipt'
  const rows = []
  const isProformaXl = isSales && invoice.invoice_type === 'proforma'
  const docHeading = isReceipt ? 'PAYMENT RECEIPT' : (isProformaXl ? 'PROFORMA INVOICE' : 'INVOICE')
  
  rows.push([docHeading, isReceipt ? invoice.receipt_number : invoice.invoice_number, '', 'Status:', isReceipt ? 'Received' : (invoice.status || 'Draft')])
  rows.push([])
  rows.push(['From', company?.name || '', '', isReceipt ? 'To' : (isSales ? 'Bill To' : 'Supplier'), contact?.name || invoice.customer_name_freeform || invoice.supplier_name_freeform || invoice.customer_name || ''])
  rows.push(['', company?.address || '', '', '', invoice.customer_address || invoice.supplier_address || ''])
  rows.push(['', company?.email || '', '', '', invoice.customer_email || invoice.supplier_email || ''])
  rows.push([])
  rows.push(['Issue Date', isReceipt ? invoice.receipt_date : invoice.invoice_date, '', isReceipt ? 'Payment Method' : 'Due Date', isReceipt ? invoice.method : (invoice.due_date || '')])
  rows.push(['Currency', invoice.currency, '', isSales ? 'Terms' : 'GSTIN', isSales ? (invoice.billing_terms || '') : (invoice.supplier_gstin || '')])
  rows.push([])
  
  if (isReceipt) {
    rows.push(['Description', 'Amount'])
    ;(items || []).forEach(it => rows.push([it.description || 'Payment Received', invoice.amount]))
    rows.push([])
    rows.push(['', 'Total Amount', invoice.amount])
  } else {
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
  const sheetName = String(isReceipt ? invoice.receipt_number : invoice.invoice_number).slice(0, 31) || 'Sheet1'
  XLSX.utils.book_append_sheet(wb, ws, sheetName)
  XLSX.writeFile(wb, `${sheetName}.xlsx`)
}

/** Exports a single invoice as a Word-compatible (.doc) file matching the same layout. */
export function exportInvoiceWord({ type, invoice, items, company, contact }) {
  const isSales = type === 'sales'
  const isReceipt = type === 'receipt'
  const isProformaDoc = isSales && invoice.invoice_type === 'proforma'
  const esc = (s) => escapeHtml(String(s ?? ''))
  
  const itemRows = (items || []).map(it => {
    if (isReceipt) {
      return `<tr><td style="padding:6px;border:1px solid #ddd;">${esc(it.description || 'Payment Received')}</td><td style="padding:6px;border:1px solid #ddd;text-align:right;">${esc(Number(it.amount || invoice.amount).toFixed(2))}</td></tr>`
    }
    return isSales
      ? `<tr><td style="padding:6px;border:1px solid #ddd;">${esc(it.description)}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.qty)}</td><td style="padding:6px;border:1px solid #ddd;">${esc(Number(it.unit_price).toFixed(2))}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.tax_percent)}%</td><td style="padding:6px;border:1px solid #ddd;">${esc(Number(it.line_total).toFixed(2))}</td></tr>`
      : `<tr><td style="padding:6px;border:1px solid #ddd;">${esc(it.product_name)}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.hsn_sac || '')}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.qty)}</td><td style="padding:6px;border:1px solid #ddd;">${esc(Number(it.unit_price).toFixed(2))}</td><td style="padding:6px;border:1px solid #ddd;">${esc(it.tax_percent)}%</td><td style="padding:6px;border:1px solid #ddd;">${esc(Number(it.line_total).toFixed(2))}</td></tr>`
  }).join('')
  
  const headerCells = isReceipt 
    ? ['Description', 'Amount'].map(c => `<th style="background:#1B3A6B;color:#fff;padding:6px;text-align:${c === 'Amount' ? 'right' : 'left'};">${esc(c)}</th>`).join('')
    : (isSales ? ['Item', 'Qty', 'Price', 'Tax %', 'Total'] : ['Product', 'HSN/SAC', 'Qty', 'Unit Price', 'Tax %', 'Total'])
        .map(c => `<th style="background:#1B3A6B;color:#fff;padding:6px;text-align:left;">${esc(c)}</th>`).join('')

  const grandTotal = Number(isSales ? invoice.amount : (invoice.net_payable ?? invoice.amount))
  const bankHtml = isSales && company?.bank_account_number ? `
    <p style="color:#999;font-size:11px;margin-top:20px;">BANK DETAILS</p>
    <p>Bank: ${esc(company.bank_name)}<br/>Account Holder: ${esc(company.bank_account_holder)}<br/>Account Number: ${esc(company.bank_account_number)}<br/>Branch: ${esc(company.bank_branch)}<br/>SWIFT: ${esc(company.bank_swift_code)}</p>
  ` : ''

  const docHeading = isReceipt ? 'Payment Receipt' : (isProformaDoc ? 'Proforma Invoice' : 'Invoice')
  const toName = isReceipt ? (contact?.name || invoice.customer_name_freeform || invoice.customer_name) : (isSales ? (contact?.name || invoice.customer_name_freeform) : (invoice.supplier_name_freeform))
  
  const html = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset="utf-8"><title>${esc(isReceipt ? invoice.receipt_number : invoice.invoice_number)}</title></head>
    <body style="font-family:Arial,sans-serif;color:#333;">
      <h1 style="margin-bottom:0;">${docHeading}</h1>
      <p style="color:#666;text-transform:uppercase;font-size:12px;">${esc(isReceipt ? 'Received' : (invoice.status || 'Draft'))}</p>
      <table style="width:100%;margin-bottom:16px;"><tr>
        <td style="vertical-align:top;width:33%;">
          <p style="color:#999;font-size:11px;">FROM</p>
          <p><strong>${esc(company?.name)}</strong><br/>${esc(company?.legal_name)}<br/>${esc(company?.address)}<br/>${esc(company?.email)}<br/>${company?.tax_id ? 'Tax ID: ' + esc(company.tax_id) : ''}</p>
        </td>
        <td style="vertical-align:top;width:33%;">
          <p style="color:#999;font-size:11px;">${isReceipt ? 'TO' : (isSales ? 'BILL TO' : 'SUPPLIER')}</p>
          <p><strong>${esc(toName)}</strong><br/>${esc(invoice.customer_address || invoice.supplier_address)}<br/>${esc(invoice.customer_email || invoice.supplier_email)}</p>
        </td>
        <td style="vertical-align:top;width:33%;">
          <p style="color:#999;font-size:11px;">DOCUMENT</p>
          <p><strong>${esc(isReceipt ? invoice.receipt_number : invoice.invoice_number)}</strong><br/>${isReceipt ? 'Date' : 'Issue'}: ${esc(isReceipt ? invoice.receipt_date : invoice.invoice_date)}<br/>${isReceipt ? 'Method: ' + esc(invoice.method || '—') : 'Due: ' + esc(invoice.due_date || '—')}<br/>Currency: ${esc(invoice.currency)}</p>
        </td>
      </tr></table>
      <table style="border-collapse:collapse;width:100%;"><thead><tr>${headerCells}</tr></thead><tbody>${itemRows}</tbody></table>
      <table style="width:100%;margin-top:12px;"><tr><td style="width:70%;"></td><td>
        ${isReceipt ? '' : `
          <p>Subtotal: ${esc((invoice.subtotal ?? invoice.amount)?.toFixed(2))} ${esc(invoice.currency)}</p>
          ${isSales && invoice.discount_value ? `<p>Discount: -${esc(Number(invoice.discount_value).toFixed(2))} ${esc(invoice.currency)}</p>` : ''}
          <p>Tax: ${esc(Number(invoice.tax_amount ?? 0).toFixed(2))} ${esc(invoice.currency)}</p>
        `}
        <p><strong>${isReceipt ? 'Total Amount' : (isSales ? 'Grand Total' : 'Net Payable')}: ${esc(Number(invoice.amount).toFixed(2))} ${esc(invoice.currency)}</strong></p>
        ${(isSales && !isReceipt) ? `<p>Paid: ${esc(Number(invoice.paid_amount || 0).toFixed(2))} ${esc(invoice.currency)}</p><p><strong>Balance Due: ${esc(Math.max(0, grandTotal - (invoice.paid_amount || 0)).toFixed(2))} ${esc(invoice.currency)}</strong></p>` : ''}
      </td></tr></table>
      ${(() => { const l = resolveLutInfo(invoice, company); return isSales && l.number ? `<p style="font-size:11px;color:#666;">The LUT acknowledgement number is ${esc(l.number)}${l.date ? ' dated ' + esc(l.date) : ''}</p>` : '' })()}
      <p style="font-size:11px;color:#666;">${esc(invoice.payment_terms || '')} ${esc(invoice.notes || '')}</p>
      ${bankHtml}
      <p style="text-align:center;color:#999;margin-top:24px;">${esc(company?.legal_name || company?.name)}</p>
    </body>
    </html>
  `
  const blob = new Blob(['﻿', html], { type: 'application/msword' })
  const fileName = String(isReceipt ? invoice.receipt_number : invoice.invoice_number) || 'document'
  downloadBlob(blob, `${fileName}.doc`)
}

/**
 * Renders a simple grouped bar chart to a PNG data URL using the Canvas API directly --
 * no charting library needed, so this works the same in the PDF/Word exports as it does
 * on screen. `series`: [{ name, color, values }], values aligned to `categories`.
 */
function renderGroupedBarChartDataUrl({ categories, series, width = 800, height = 400, valueFormatter }) {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, width, height)

  const marginLeft = 64, marginRight = 20, marginTop = 20, marginBottom = 66
  const chartW = width - marginLeft - marginRight
  const chartH = height - marginTop - marginBottom

  const allValues = series.flatMap(s => s.values)
  const maxVal = Math.max(1, ...allValues, 0)
  const minVal = Math.min(0, ...allValues)
  const range = maxVal - minVal || 1
  const zeroY = marginTop + chartH * (maxVal / range)

  ctx.strokeStyle = '#e2e8f0'
  ctx.fillStyle = '#94a3b8'
  ctx.font = '10px sans-serif'
  ctx.textAlign = 'right'
  const ticks = 5
  for (let t = 0; t <= ticks; t++) {
    const val = minVal + (range * t) / ticks
    const y = marginTop + chartH - ((val - minVal) / range) * chartH
    ctx.beginPath(); ctx.moveTo(marginLeft, y); ctx.lineTo(marginLeft + chartW, y); ctx.stroke()
    ctx.fillText(valueFormatter ? valueFormatter(val) : Math.round(val).toLocaleString(), marginLeft - 6, y + 3)
  }

  const groupWidth = chartW / Math.max(categories.length, 1)
  const barPadding = groupWidth * 0.15
  const barWidth = (groupWidth - barPadding * 2) / Math.max(series.length, 1)

  categories.forEach((cat, ci) => {
    series.forEach((s, si) => {
      const val = s.values[ci] || 0
      const barH = (Math.abs(val) / range) * chartH
      const x = marginLeft + ci * groupWidth + barPadding + si * barWidth
      const y = val >= 0 ? zeroY - barH : zeroY
      ctx.fillStyle = s.color
      ctx.fillRect(x, y, Math.max(barWidth - 2, 1), barH)
    })
    ctx.fillStyle = '#475569'
    ctx.textAlign = 'center'
    ctx.font = '10px sans-serif'
    ctx.fillText(cat, marginLeft + ci * groupWidth + groupWidth / 2, marginTop + chartH + 16)
  })

  ctx.strokeStyle = '#94a3b8'
  ctx.beginPath(); ctx.moveTo(marginLeft, zeroY); ctx.lineTo(marginLeft + chartW, zeroY); ctx.stroke()

  let legendX = marginLeft
  const legendY = height - 20
  ctx.textAlign = 'left'
  ctx.font = '11px sans-serif'
  series.forEach(s => {
    ctx.fillStyle = s.color
    ctx.fillRect(legendX, legendY - 9, 10, 10)
    ctx.fillStyle = '#334155'
    ctx.fillText(s.name, legendX + 14, legendY)
    legendX += ctx.measureText(s.name).width + 40
  })

  return canvas.toDataURL('image/png')
}

/**
 * Multi-section report export -- used by the "choose what to include" Download Report
 * flow on every page (Dashboard, Chart of Accounts, Analytics, etc). Each section is
 * a data table ({ heading, columns, rows }), summary key/value pairs
 * ({ heading, keyValuePairs: [[label, value], ...] }), or a chart
 * ({ heading, chart: { categories, series } }).
 */
export async function exportMultiSectionPDF({ title, subtitle, sections, filename, logoUrl, preview = false }) {
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
  
  let loadedLogo = null
  if (logoUrl) {
    loadedLogo = await loadImageAsDataUrl(logoUrl)
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
      let columnStyles = {}
      if (section.columns.length === 3) {
        columnStyles = { 0: { cellWidth: 102 }, 1: { cellWidth: 40, halign: 'right' }, 2: { cellWidth: 40, halign: 'right' } }
      } else if (section.columns.length === 2) {
        columnStyles = { 0: { cellWidth: 142 }, 1: { cellWidth: 40, halign: 'right' } }
      }
      
      const safeHead = section.columns.map((c, i) => {
        const text = sanitizeText(c)
        return (i > 0) ? { content: text, styles: { halign: 'right' } } : text
      })
      const safeBody = section.rows.map(row => row.map(sanitizeText))

      autoTable(doc, {
        startY: y + 3,
        head: [safeHead],
        body: safeBody,
        headStyles: { fillColor: section.headColor || [27, 58, 107], fontSize: 8 },
        styles: { fontSize: 8, cellPadding: 2.5 },
        columnStyles: columnStyles,
        margin: { left: 14, right: 14 },
      })
      y = doc.lastAutoTable.finalY + 10
    } else if (section.chart) {
      const imgW = pageWidth - 28
      const imgH = imgW * (400 / 800)
      if (y + imgH > pageHeight - 15) { doc.addPage(); y = 20 }
      const dataUrl = renderGroupedBarChartDataUrl({ ...section.chart, valueFormatter: section.chart.valueFormatter })
      doc.addImage(dataUrl, 'PNG', 14, y + 3, imgW, imgH)
      y += imgH + 12
    }
  })

  const pageCount = doc.internal.getNumberOfPages()
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i)
    if (loadedLogo?.dataUrl) {
      const logoH = 12
      const logoW = logoH * loadedLogo.ratio
      doc.addImage(loadedLogo.dataUrl, 'PNG', pageWidth - 14 - logoW, 10, logoW, logoH)
    }
  }

  if (preview) {
    const blob = doc.output('blob')
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } else {
    doc.save(`${filename}.pdf`)
  }
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
    } else if (section.chart) {
      rows.push(['(Chart shown as data -- Excel export cannot embed a native chart image)'])
      rows.push(['Category', ...section.chart.series.map(s => s.name)])
      section.chart.categories.forEach((cat, i) => rows.push([cat, ...section.chart.series.map(s => s.values[i])]))
    }
    rows.push([])
  })
  const ws = XLSX.utils.aoa_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, title.slice(0, 31) || 'Report')
  XLSX.writeFile(wb, `${filename}.xlsx`)
}

/** Multi-section Word export. */
export function exportMultiSectionWord({ title, subtitle, sections, filename, logoUrl }) {
  const esc = escapeHtml
  const sectionsHtml = sections.map(section => {
    let inner = ''
    if (section.keyValuePairs) {
      inner = section.keyValuePairs.map(([label, val]) =>
        `<p style="margin:2px 0;"><strong>${esc(label)}:</strong> ${esc(val)}</p>`
      ).join('')
    } else if (section.columns && section.rows) {
      const rgb = section.headColor || [27, 58, 107]
      const bgColor = `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`
      
      const head = section.columns.map((c, i) => {
        const align = (i > 0) ? 'right' : 'left'
        const width = (section.columns.length === 3 && i > 0) ? 'width:15%;' : ((section.columns.length === 2 && i > 0) ? 'width:20%;' : 'width:auto;')
        return `<th style="background:${bgColor};color:#fff;padding:5px 8px;text-align:${align};${width}">${esc(c)}</th>`
      }).join('')
      
      const body = section.rows.map(r =>
        `<tr>${r.map((cell, i) => {
          const align = (i > 0) ? 'right' : 'left'
          return `<td style="padding:5px 8px;border:1px solid #ddd;text-align:${align};">${esc(cell)}</td>`
        }).join('')}</tr>`
      ).join('')
      inner = `<table style="border-collapse:collapse;width:100%;margin-bottom:12px;"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`
    } else if (section.chart) {
      const dataUrl = renderGroupedBarChartDataUrl(section.chart)
      inner = `<img src="${dataUrl}" style="max-width:100%;margin-bottom:12px;" />`
    }
    return `<h3 style="color:#1B3A6B;margin-top:20px;">${esc(section.heading)}</h3>${inner}`
  }).join('')

  const html = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset="utf-8"><title>${esc(title)}</title></head>
    <body style="font-family:Arial,sans-serif;">
      ${logoUrl ? `<img src="${logoUrl}" style="max-height:50px;float:right;" />` : ''}
      <h1 style="color:#1B3A6B;margin-bottom:0;">${esc(title)}</h1>
      ${subtitle ? `<p style="color:#666;">${esc(subtitle)}</p>` : ''}
      ${sectionsHtml}
    </body>
    </html>
  `
  const blob = new Blob(['\ufeff', html], { type: 'application/msword' })
  downloadBlob(blob, `${filename}.doc`)
}

export async function exportReceiptPDF({ invoice: receipt, company, contact, preview = false }) {
  const doc = new jsPDF()
  const pageWidth = doc.internal.pageSize.getWidth()
  const rightX = pageWidth - 14
  
  const logo = await loadImageAsDataUrl(company?.logo_url)
  
  // Top Right: PAYMENT RECEIPT
  doc.setFontSize(22)
  doc.setTextColor(16, 185, 129) // emerald-500
  doc.setFont(undefined, 'bold')
  doc.text('PAYMENT RECEIPT', rightX, 22, { align: 'right' })
  
  // Receipt details below PAYMENT RECEIPT
  doc.setFontSize(10)
  doc.setTextColor(90)
  doc.setFont(undefined, 'normal')
  let currentRightY = 32
  doc.text(`Receipt #:`, rightX - 35, currentRightY, { align: 'right' })
  doc.setTextColor(20)
  doc.setFont(undefined, 'bold')
  doc.text(String(receipt.receipt_number || ''), rightX, currentRightY, { align: 'right' })
  
  currentRightY += 6
  doc.setTextColor(90)
  doc.setFont(undefined, 'normal')
  doc.text(`Date:`, rightX - 35, currentRightY, { align: 'right' })
  doc.setTextColor(20)
  doc.setFont(undefined, 'bold')
  doc.text(String(receipt.receipt_date || ''), rightX, currentRightY, { align: 'right' })
  
  if (receipt.invoice?.invoice_number || receipt.invoice_link) {
    currentRightY += 6
    doc.setTextColor(90)
    doc.setFont(undefined, 'normal')
    doc.text(`Invoice Ref:`, rightX - 35, currentRightY, { align: 'right' })
    doc.setTextColor(20)
    doc.setFont(undefined, 'bold')
    const ref = receipt.invoice?.invoice_number || receipt.invoice_link || ''
    // Handle JSON object link to invoice if applicable
    let refStr = typeof ref === 'string' ? ref : (ref.invoice_number || '')
    doc.text(refStr, rightX, currentRightY, { align: 'right' })
  }

  // Top Left: Logo and Company Details
  let currentLeftY = 14
  if (logo?.dataUrl) {
    const logoH = 12
    const logoW = logoH * logo.ratio
    doc.addImage(logo.dataUrl, 'PNG', 14, currentLeftY, logoW, logoH)
    currentLeftY += logoH + 8
  } else {
    currentLeftY += 8
  }

  doc.setFontSize(14)
  doc.setTextColor(20)
  doc.setFont(undefined, 'bold')
  doc.text(company?.name || '', 14, currentLeftY)
  currentLeftY += 6
  
  doc.setFontSize(9)
  doc.setFont(undefined, 'normal')
  doc.setTextColor(90)
  const companyLines = [
    (company?.legal_name || '').trim(),
    (company?.address || '').trim(),
    [company?.city, company?.country].filter(Boolean).join(', ').trim(),
    (company?.email || '').trim(), 
    (company?.phone || '').trim(), 
    (company?.website || '').trim(),
    company?.tax_id ? `GSTIN: ${company.tax_id}` : null,
  ].filter(Boolean)
  
  companyLines.forEach(line => {
    doc.text(line, 14, currentLeftY)
    currentLeftY += 5
  })
  
  // LUT Info if present
  const lutInfo = resolveLutInfo(receipt, company)
  if (lutInfo.number) {
    doc.text(`LUT: ${lutInfo.number}`, 14, currentLeftY)
    currentLeftY += 5
  }

  // Green separator line
  let y = Math.max(currentLeftY, currentRightY) + 8
  doc.setDrawColor(16, 185, 129)
  doc.setLineWidth(0.5)
  doc.line(14, y, rightX, y)
  y += 10
  
  // RECEIVED FROM section
  doc.setFontSize(9)
  doc.setTextColor(150)
  doc.setFont(undefined, 'bold')
  doc.text('RECEIVED FROM', 14, y)
  y += 6
  
  doc.setFontSize(11)
  doc.setTextColor(20)
  const customerName = contact?.name || receipt.customer_name_freeform || receipt.customer_name || ''
  doc.text(customerName, 14, y)
  y += 5
  
  doc.setFontSize(9)
  doc.setTextColor(90)
  doc.setFont(undefined, 'normal')
  const address = receipt.customer_address || contact?.address || ''
  if (address) {
    const wrappedAddress = doc.splitTextToSize(`Address: ${address}`, rightX - 14)
    doc.text(wrappedAddress, 14, y)
    y += wrappedAddress.length * 4.5
  }
  
  const email = receipt.customer_email || contact?.email || ''
  const phone = receipt.customer_phone || contact?.phone || ''
  const parts = []
  if (email) parts.push(`Email: ${email}`)
  if (phone) parts.push(`Phone: ${phone}`)
  if (parts.length > 0) {
    doc.text(parts.join('    '), 14, y)
    y += 5
  }
  
  y += 6

  // Table
  const tableRows = [
    [
      `Payment received${(receipt.invoice?.invoice_number || typeof receipt.invoice_link === 'string') ? ` for Invoice ${receipt.invoice?.invoice_number || receipt.invoice_link}` : ''}`,
      receipt.method || 'Bank Transfer',
      `${Number(receipt.amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${receipt.currency}`
    ]
  ]

  autoTable(doc, {
    startY: y,
    head: [['DESCRIPTION', 'PAYMENT METHOD', 'AMOUNT']],
    body: tableRows,
    headStyles: { fillColor: [248, 250, 252], textColor: [100, 116, 139], fontSize: 9, fontStyle: 'bold' },
    bodyStyles: { fontSize: 10, textColor: [20, 20, 20] },
    columnStyles: { 
      0: { cellWidth: 90 },
      2: { halign: 'right', fontStyle: 'bold' }
    },
    theme: 'plain',
    margin: { left: 14, right: 14 }
  })
  
  let finalY = doc.lastAutoTable.finalY + 2
  
  // Total Amount Received Row (Green background)
  doc.setFillColor(236, 253, 245) // emerald-50
  doc.rect(14, finalY, pageWidth - 28, 12, 'F')
  doc.setFontSize(11)
  doc.setFont(undefined, 'bold')
  doc.setTextColor(20, 20, 20)
  doc.text('Total Amount Received', 18, finalY + 8)
  
  doc.setTextColor(16, 185, 129) // emerald-500
  doc.text(`${Number(receipt.amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${receipt.currency}`, rightX - 4, finalY + 8, { align: 'right' })
  
  finalY += 40
  
  // Signatory
  doc.setDrawColor(0)
  doc.setLineWidth(0.3)
  doc.line(rightX - 50, finalY, rightX, finalY)
  finalY += 5
  doc.setFontSize(9)
  doc.setFont(undefined, 'normal')
  doc.setTextColor(100, 116, 139)
  doc.text('Authorized Signatory', rightX - 25, finalY, { align: 'center' })
  finalY += 5
  doc.setFontSize(10)
  doc.setFont(undefined, 'bold')
  doc.setTextColor(20, 20, 20)
  doc.text(company?.name || '', rightX - 25, finalY, { align: 'center' })
  
  // Footer
  doc.setFontSize(8)
  doc.setFont(undefined, 'normal')
  doc.setTextColor(148, 163, 184)
  doc.text('This is a computer-generated receipt and is valid without a physical signature.', pageWidth / 2, doc.internal.pageSize.getHeight() - 15, { align: 'center' })

  if (preview) {
    window.open(doc.output('bloburl'), '_blank')
  } else {
    doc.save(`${receipt.receipt_number || 'Receipt'}.pdf`)
  }
}

export function exportReceiptWord({ invoice: receipt, company, contact }) {
  const esc = (s) => escapeHtml(String(s ?? ''))
  const customerName = contact?.name || receipt.customer_name_freeform || receipt.customer_name || ''
  const address = receipt.customer_address || contact?.address || ''
  const email = receipt.customer_email || contact?.email || ''
  const phone = receipt.customer_phone || contact?.phone || ''
  
  let refStr = ''
  if (receipt.invoice?.invoice_number || receipt.invoice_link) {
    const ref = receipt.invoice?.invoice_number || receipt.invoice_link || ''
    refStr = typeof ref === 'string' ? ref : (ref.invoice_number || '')
  }

  const html = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset="utf-8"><title>${esc(receipt.receipt_number)}</title></head>
    <body style="font-family:Arial,sans-serif;color:#333;">
      <table style="width:100%;margin-bottom:20px;"><tr>
        <td style="vertical-align:top;width:60%;">
          <h2 style="margin:0;color:#333;">${esc(company?.name)}</h2>
          <p style="color:#666;font-size:12px;margin:4px 0;">${esc(company?.legal_name)}<br/>${esc(company?.address)}<br/>${esc(company?.email)}<br/>${company?.tax_id ? 'GSTIN: ' + esc(company.tax_id) : ''}</p>
        </td>
        <td style="vertical-align:top;width:40%;text-align:right;">
          <h1 style="margin:0;color:#10B981;">PAYMENT RECEIPT</h1>
          <p style="color:#666;font-size:12px;margin:4px 0;">
            Receipt #: <strong>${esc(receipt.receipt_number)}</strong><br/>
            Date: <strong>${esc(receipt.receipt_date)}</strong>
            ${refStr ? `<br/>Invoice Ref: <strong>${esc(refStr)}</strong>` : ''}
          </p>
        </td>
      </tr></table>
      
      <hr style="border:none;border-top:2px solid #10B981;margin:20px 0;" />
      
      <p style="color:#999;font-size:12px;font-weight:bold;margin-bottom:4px;">RECEIVED FROM</p>
      <h3 style="margin:0;">${esc(customerName)}</h3>
      ${address ? `<p style="margin:4px 0;font-size:12px;color:#666;">Address: ${esc(address)}</p>` : ''}
      <p style="margin:4px 0;font-size:12px;color:#666;">
        ${email ? `Email: ${esc(email)} &nbsp;&nbsp;&nbsp;` : ''}
        ${phone ? `Phone: ${esc(phone)}` : ''}
      </p>
      
      <table style="border-collapse:collapse;width:100%;margin-top:20px;">
        <thead>
          <tr style="background:#f8fafc;color:#64748b;">
            <th style="padding:10px;text-align:left;">DESCRIPTION</th>
            <th style="padding:10px;text-align:left;">PAYMENT METHOD</th>
            <th style="padding:10px;text-align:right;">AMOUNT</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="padding:10px;border-bottom:1px solid #e2e8f0;">Payment received${refStr ? ` for Invoice ${esc(refStr)}` : ''}</td>
            <td style="padding:10px;border-bottom:1px solid #e2e8f0;">${esc(receipt.method || 'Bank Transfer')}</td>
            <td style="padding:10px;border-bottom:1px solid #e2e8f0;text-align:right;font-weight:bold;">${esc(Number(receipt.amount).toFixed(2))} ${esc(receipt.currency)}</td>
          </tr>
        </tbody>
      </table>
      
      <table style="width:100%;margin-top:20px;background:#ecfdf5;">
        <tr>
          <td style="padding:15px;font-weight:bold;font-size:14px;">Total Amount Received</td>
          <td style="padding:15px;text-align:right;font-weight:bold;font-size:14px;color:#10B981;">${esc(Number(receipt.amount).toFixed(2))} ${esc(receipt.currency)}</td>
        </tr>
      </table>
      
      <table style="width:100%;margin-top:60px;">
        <tr>
          <td style="width:60%;"></td>
          <td style="width:40%;text-align:center;">
            <hr style="border:none;border-top:1px solid #000;margin-bottom:5px;" />
            <p style="margin:0;color:#64748b;font-size:12px;">Authorized Signatory</p>
            <p style="margin:5px 0 0 0;font-weight:bold;font-size:14px;">${esc(company?.name)}</p>
          </td>
        </tr>
      </table>
      
      <p style="text-align:center;color:#94a3b8;font-size:11px;margin-top:40px;">This is a computer-generated receipt and is valid without a physical signature.</p>
    </body>
    </html>
  `
  const blob = new Blob(['﻿', html], { type: 'application/msword' })
  downloadBlob(blob, `${receipt.receipt_number || 'Receipt'}.doc`)
}
