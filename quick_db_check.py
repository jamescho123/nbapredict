import psycopg2

try:
    conn = psycopg2.connect(host='localhost', dbname='James', user='postgres', password='jcjc1749')
    cur = conn.cursor()
    
    # Get tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'NBA' ORDER BY table_name;")
    tables = [row[0] for row in cur.fetchall()]
    print("Tables:", tables)
    
    # Check each table
    for table in tables:
        cur.execute(f'SELECT COUNT(*) FROM "NBA"."{table}";')
        count = cur.fetchone()[0]
        print(f"{table}: {count} rows")
        
        if count > 0:
            cur.execute(f'SELECT * FROM "NBA"."{table}" LIMIT 1;')
            sample = cur.fetchone()
            print(f"  Sample: {sample}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
