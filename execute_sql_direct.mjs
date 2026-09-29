import { createClient } from '@supabase/supabase-js';
import fs from 'fs';

const supabase = createClient('https://pxygyucscjmvgvfilohq.supabase.co', 'sb_publishable_daz-WI4nSsASBYZHVNkQyA_Z4IAl7QO');
// The anon key can't execute raw SQL!
