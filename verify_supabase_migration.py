import psycopg2

supabase_conn_params = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'VXUXqY9Uofg9ujoo',
    'port': 5432
}

def verify_migration():
    conn = psycopg2.connect(**supabase_conn_params)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'NBA'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables in NBA schema:")
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT COUNT(*) FROM "NBA"."{table_name}";')
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count} rows")
    
    conn.close()

if __name__ == "__main__":
    verify_migration()

