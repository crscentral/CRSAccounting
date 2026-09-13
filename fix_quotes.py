import os
import glob

for filepath in glob.glob("src/pages/*.jsx"):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix the literal backslash error
    content = content.replace("format === \\'pdf\\' || format === \\'preview\\'", "format === 'pdf' || format === 'preview'")
    
    with open(filepath, 'w') as f:
        f.write(content)

print("Fixed quotes")
