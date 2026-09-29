import re

def patch():
    with open('src/pages/HotelExpenses.jsx', 'r') as f:
        content = f.read()

    # Replace .eq('product', activeProduct) with .in('product', ['hotel', 'restaurant']) for the fetches
    
    # In loadAll:
    # supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct)
    content = content.replace("supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct)",
                              "supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant'])")
    
    # supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    content = content.replace("supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)",
                              "supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant'])")

    # supabase.from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)').eq('company_id', activeCompany.id).eq('product', activeProduct)
    content = content.replace("supabase.from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)').eq('company_id', activeCompany.id).eq('product', activeProduct)",
                              "supabase.from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant'])")

    # Note: we probably shouldn't change accounts because then we get duplicate accounts if they exist in both.
    # Wait, if we don't change accounts, the form dropdown for "Expense Head" won't show Restaurant-only accounts.
    # But usually the user creates accounts in the active product. If they are in Hotel, they use Hotel accounts.
    # The existing entries will still render fine because the join `account:accounts(code, name, subtype)` fetches the referenced account regardless of product!
    
    # Let's also do it for the report generator fetch:
    # const { data: exp } = await supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct)
    # The replace above will catch this as well!

    with open('src/pages/HotelExpenses.jsx', 'w') as f:
        f.write(content)
        print("Patched HotelExpenses.jsx")

patch()
