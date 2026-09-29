import { createClient } from '@supabase/supabase-js';
const supabase = createClient('https://pxygyucscjmvgvfilohq.supabase.co', 'sb_publishable_daz-WI4nSsASBYZHVNkQyA_Z4IAl7QO');

async function check() {
  const { data } = await supabase.from('accounts').select('id, name, code, product');
  const ar = data.filter(d => d.name.toLowerCase().includes('receivable'));
  console.log(ar);
}
check();
