import json
import collections

with open('accounts.json', 'r') as f:
    data = json.load(f)

accounts = {}
for r in data:
    key = (r['product'], r['code'], r['name'])
    accounts[key] = r

product_accounts = collections.defaultdict(list)
for key, r in accounts.items():
    product_accounts[r['product']].append(r)

name_to_code = {}
next_code = {'Assets': 1100, 'Liabilities': 2100, 'Equity': 3100, 'Revenue': 4100, 'Expenses': 5100}
taken_codes = set()

# Process Basic
for r in sorted(product_accounts['basic'], key=lambda x: x['code']):
    if r['name'] not in name_to_code:
        name_to_code[r['name']] = r['code']
        taken_codes.add(r['code'])
    r['new_code'] = name_to_code[r['name']]

# Hotel
for r in sorted(product_accounts['hotel'], key=lambda x: x['code']):
    if r['name'] not in name_to_code:
        code = r['code']
        if code in taken_codes:
            c = next_code[r['type']]
            while str(c) in taken_codes:
                c += 1
            code = str(c)
            next_code[r['type']] = c + 1
        name_to_code[r['name']] = code
        taken_codes.add(code)
    r['new_code'] = name_to_code[r['name']]

# Restaurant
for r in sorted(product_accounts['restaurant'], key=lambda x: x['code']):
    if r['name'] not in name_to_code:
        code = r['code']
        if code in taken_codes:
            c = next_code[r['type']]
            while str(c) in taken_codes:
                c += 1
            code = str(c)
            next_code[r['type']] = c + 1
        name_to_code[r['name']] = code
        taken_codes.add(code)
    r['new_code'] = name_to_code[r['name']]

print("Total unique names:", len(name_to_code))
for r in accounts.values():
    if r['code'] != r['new_code']:
        print(f"Product: {r['product']}, Name: {r['name']}, Old Code: {r['code']}, New Code: {r['new_code']}")

# write sql file
with open('update_codes.sql', 'w') as f:
    f.write("-- Unifying codes\n")
    for r in accounts.values():
        if r['code'] != r['new_code']:
            name_esc = r['name'].replace("'", "''")
            f.write(f"UPDATE public.accounts SET code = '{r['new_code']}' WHERE product = '{r['product']}' AND name = '{name_esc}';\n")

