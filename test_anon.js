require('dotenv').config({ path: '/Users/sumantsingh/.gemini/antigravity/brain/a101a607-397b-4a80-b151-c0b335335fd5/scratch/CRSAccounting/.env' })
const { createClient } = require('@supabase/supabase-js');
console.log("Fetching...", process.env.VITE_SUPABASE_URL);
