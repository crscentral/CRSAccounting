import os
import glob
import re

for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith(('.js', '.jsx')):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()

            if "toISOString" in content:
                # If it's fiscalYear.js, skip because we already fixed it
                if path == "src/lib/fiscalYear.js":
                    continue
                
                # Check for various ISO string replacements
                if "new Date().toISOString().slice(0, 10)" in content or "new Date().toISOString().split('T')[0]" in content or "editingRow?.stat_date || new Date().toISOString().slice(0, 10)" in content or "new Date(today).toISOString().slice(0, 10)" in content:
                    
                    # Ensure we have the import
                    if "import { getLocalDate } from" not in content:
                        # find right relative path
                        depth = path.count('/') - 1
                        prefix = '../' * depth if depth > 0 else './'
                        if path.startswith('src/lib/'):
                            prefix = './'
                        import_stmt = f"import {{ getLocalDate }} from '{prefix}lib/dateUtils'\n"
                        
                        # Add import after the first import or at top
                        if "import " in content:
                            content = content.replace("import ", import_stmt + "import ", 1)
                        else:
                            content = import_stmt + content
                
                # Replace new Date().toISOString().slice(0, 10) -> getLocalDate()
                content = content.replace("new Date().toISOString().slice(0, 10)", "getLocalDate()")
                
                # Replace today.toISOString().slice(0, 10) -> getLocalDate(today)
                content = content.replace("today.toISOString().slice(0, 10)", "getLocalDate(today)")
                
                # Replace d.toISOString().slice(0, 10) -> getLocalDate(d)
                content = content.replace("d.toISOString().slice(0, 10)", "getLocalDate(d)")

                # Any lingering new Date(today).toISOString().slice(0, 10)
                content = content.replace("new Date(today).toISOString().slice(0, 10)", "getLocalDate(new Date(today))")

                # HotelOccupancyStats has `const s = d.toISOString().slice(0, 10)`
                
                with open(path, 'w') as f:
                    f.write(content)
