import re

with open('src/pages/SalesInvoices.jsx', 'r') as f:
    content = f.read()

old_modal = """      <PaymentReceiptFormModal
        open={receiptModalOpen}
        onClose={() => setReceiptModalOpen(false)}
        companyId={activeCompany?.id}
        product={activeProduct}
        initialData={editingReceipt}
        onSuccess={loadData}
        invoices={invoices}
      />"""

new_modal = """      {receiptModalOpen && (
        <PaymentReceiptFormModal
          open={receiptModalOpen}
          onClose={() => setReceiptModalOpen(false)}
          companyId={activeCompany?.id}
          product={activeProduct}
          initialData={editingReceipt}
          onSuccess={loadData}
          invoices={invoices}
        />
      )}"""

content = content.replace(old_modal, new_modal)

with open('src/pages/SalesInvoices.jsx', 'w') as f:
    f.write(content)
