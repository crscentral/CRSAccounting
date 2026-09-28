import psycopg2

try:
    conn = psycopg2.connect("postgresql://postgres:Hideaway%4024280@db.pxygyucscjmvgvfilohq.supabase.co:5432/postgres")
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
