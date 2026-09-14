with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

code = code.replace(
    ".replace(/[^ - ]/g, ''); // Strip remaining unsupported unicode for jsPDF",
    r".replace(/[^\x00-\x7F]/g, ''); // Strip remaining unsupported unicode for jsPDF"
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
