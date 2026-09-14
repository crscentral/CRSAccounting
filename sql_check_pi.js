import fs from 'fs';
const payload = JSON.stringify({
  project_id: 'pxygyucscjmvgvfilohq',
  query: "SELECT column_name FROM information_schema.columns WHERE table_name = 'purchase_invoices'"
});
fs.writeFileSync('pi_payload.json', payload);
