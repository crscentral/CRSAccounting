import { createClient } from '@supabase/supabase-js';
const supabaseUrl = 'https://pxygyucscjmvgvfilohq.supabase.co';
const supabaseAnonKey = 'sb_publishable_daz-WI4nSsASBYZHVNkQyA_Z4IAl7QO';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function run() {
  const { data: entries } = await supabase.from('restaurant_daily_revenue').select('*');
  console.log(entries);
}
run();
