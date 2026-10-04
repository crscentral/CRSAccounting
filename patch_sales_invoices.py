with open("src/pages/SalesInvoices.jsx", "r") as f:
    content = f.read()

content = content.replace("invoices={invoices}", "invoices={invoices}\n          contacts={contacts}")

with open("src/pages/SalesInvoices.jsx", "w") as f:
    f.write(content)

