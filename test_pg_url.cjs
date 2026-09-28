const parse = require('pg-connection-string').parse;
const url = "postgresql://postgres:Hideaway%4024280@db.pxygyucscjmvgvfilohq.supabase.co:5432/postgres?sslmode=require";
console.log(parse(url));
