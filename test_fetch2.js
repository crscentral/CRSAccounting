require('dotenv').config({ path: '.env.local' });
const { createClient } = require('@supabase/supabase-js');

(async () => {
  const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_SERVICE_ROLE_KEY);
  const { data, error } = await supabase
      .from('companies')
      .select('*, members:company_members(role, user_id, profile:user_profiles(email, full_name))')
      .eq('approval_status', 'pending');
  console.log('Error:', error);
  console.log('Data Length:', data ? data.length : 0);
})();
