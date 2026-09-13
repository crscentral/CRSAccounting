import fs from 'fs';
import { execSync } from 'child_process';

const sql = fs.readFileSync('capital_migration.sql', 'utf8');
const escapedSql = JSON.stringify(sql);
const payload = JSON.stringify({
  project_id: 'pxygyucscjmvgvfilohq',
  query: sql
});
fs.writeFileSync('payload.json', payload);
