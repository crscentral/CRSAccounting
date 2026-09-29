import json

with open('accounts.json', 'r') as f:
    data = json.load(f)

# Deduplicate by (product, code, name) for the base template
base_accounts = []
seen = set()
for r in data:
    key = (r['product'], r['code'], r['name'])
    if key not in seen:
        seen.add(key)
        base_accounts.append(r)

# Unify codes
name_to_code = {}
next_code = {'Assets': 1100, 'Liabilities': 2100, 'Equity': 3100, 'Revenue': 4100, 'Expenses': 5100}
taken_codes = set()

# Process Basic first (preserve as much as possible)
for r in sorted([a for a in base_accounts if a['product'] == 'basic'], key=lambda x: x['code']):
    if r['name'] not in name_to_code:
        # Keep original code if possible
        if r['code'] not in taken_codes:
            name_to_code[r['name']] = r['code']
            taken_codes.add(r['code'])
        else:
            c = next_code[r['type']]
            while str(c) in taken_codes:
                c += 1
            name_to_code[r['name']] = str(c)
            taken_codes.add(str(c))
            next_code[r['type']] = c + 1
    r['new_code'] = name_to_code[r['name']]

# Hotel
for r in sorted([a for a in base_accounts if a['product'] == 'hotel'], key=lambda x: x['code']):
    if r['name'] not in name_to_code:
        if r['code'] not in taken_codes:
            name_to_code[r['name']] = r['code']
            taken_codes.add(r['code'])
        else:
            c = next_code[r['type']]
            while str(c) in taken_codes:
                c += 1
            name_to_code[r['name']] = str(c)
            taken_codes.add(str(c))
            next_code[r['type']] = c + 1
    r['new_code'] = name_to_code[r['name']]

# Restaurant
for r in sorted([a for a in base_accounts if a['product'] == 'restaurant'], key=lambda x: x['code']):
    if r['name'] not in name_to_code:
        if r['code'] not in taken_codes:
            name_to_code[r['name']] = r['code']
            taken_codes.add(r['code'])
        else:
            c = next_code[r['type']]
            while str(c) in taken_codes:
                c += 1
            name_to_code[r['name']] = str(c)
            taken_codes.add(str(c))
            next_code[r['type']] = c + 1
    r['new_code'] = name_to_code[r['name']]

sql = "-- 1. Update existing accounts to use unified codes\n"
for r in base_accounts:
    if r['code'] != r['new_code']:
        name_esc = r['name'].replace("'", "''")
        sql += f"UPDATE public.accounts SET code = '{r['new_code']}' WHERE product = '{r['product']}' AND name = '{name_esc}';\n"

sql += "\n\n-- 2. Create trigger to seed accounts for new companies\n"
sql += "create or replace function public.seed_default_accounts()\n"
sql += "returns trigger language plpgsql security definer as $$\n"
sql += "begin\n"
sql += "  insert into public.accounts (company_id, product, code, name, type, subtype, currency)\n"
sql += "  values\n"

values = []
for r in base_accounts:
    name_esc = r['name'].replace("'", "''")
    subtype = f"'{r['subtype'].replace(chr(39), chr(39)+chr(39))}'" if r['subtype'] else 'null'
    values.append(f"  (new.id, '{r['product']}', '{r['new_code']}', '{name_esc}', '{r['type']}', {subtype}, coalesce(new.base_currency, 'USD'))")

sql += ",\n".join(values)
sql += ";\n"
sql += "  return new;\n"
sql += "end;\n"
sql += "$$;\n\n"
sql += "drop trigger if exists trg_seed_default_accounts on public.companies;\n"
sql += "create trigger trg_seed_default_accounts\n"
sql += "  after insert on public.companies\n"
sql += "  for each row execute function public.seed_default_accounts();\n"

with open('supabase/migrations/23_unify_and_seed_accounts.sql', 'w') as f:
    f.write(sql)

