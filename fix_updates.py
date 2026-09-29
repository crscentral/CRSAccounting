with open('supabase/migrations/23_unify_and_seed_accounts.sql', 'r') as f:
    sql = f.read()

# find the update block
import re
updates = re.findall(r"UPDATE public.accounts SET code = '(.*?)' WHERE product = '(.*?)' AND name = '(.*?)';", sql)

out_sql = "-- 1. Temp codes\n"
for new_code, product, name in updates:
    name_esc = name.replace("'", "''")
    out_sql += f"UPDATE public.accounts SET code = 'T_{new_code}' WHERE product = '{product}' AND name = '{name_esc}';\n"

out_sql += "\n-- 2. Final codes\n"
for new_code, product, name in updates:
    name_esc = name.replace("'", "''")
    out_sql += f"UPDATE public.accounts SET code = '{new_code}' WHERE product = '{product}' AND name = '{name_esc}';\n"

# replace the original update block
sql = re.sub(r"UPDATE public.accounts SET code = '.*?' WHERE product = '.*?' AND name = '.*?';\n", "", sql)
sql = sql.replace("-- 1. Update existing accounts to use unified codes\n", out_sql)

with open('supabase/migrations/23_unify_and_seed_accounts.sql', 'w') as f:
    f.write(sql)
