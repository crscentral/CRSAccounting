import { createClient } from '@supabase/supabase-js';
import fs from 'fs';

const supabase = createClient('https://pxygyucscjmvgvfilohq.supabase.co', 'sb_publishable_daz-WI4nSsASBYZHVNkQyA_Z4IAl7QO');

async function run() {
  const { data: accounts, error } = await supabase
    .from('accounts')
    .select('id, company_id, product, code, name, type, subtype')
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
