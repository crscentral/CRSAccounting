const { Client } = require('pg');

const client = new Client({
  connectionString: "postgresql://postgres:Hideaway%4024280@db.pxygyucscjmvgvfilohq.supabase.co:5432/postgres"
});

client.connect()
  .then(() => {
    console.log("Connected successfully!");
    client.end();
  })
  .catch(err => console.error("Connection error", err.stack));
