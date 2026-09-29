require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_ANON_KEY);

async function run() {
  const { data: accounts, error } = await supabase
    .from('accounts')
    .select('product, code, name, type, subtype')
    .order('product', { ascending: true })
    .order('code', { ascending: true });
    
  if (error) {
    console.error(error);
    return;
  }
  
  fs.writeFileSync('accounts.json', JSON.stringify(accounts, null, 2));
  console.log("Wrote accounts.json");
}

run();
