import json

with open('supabase/migrations/23_unify_and_seed_accounts.sql', 'r') as f:
    sql = f.read()

print(json.dumps(sql))
