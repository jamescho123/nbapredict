"""
Use Supabase Connection Pooler instead of direct connection
The connection pooler has IPv4 address which works better with Python
"""

import psycopg2

print("=" * 60)
print("Connecting via Supabase Connection Pooler")
print("=" * 60)
print()

# Connection Pooler (IPv4 compatible)
pooler_conn_params = {
    'host': 'mxnpfsiyaqqwdcokukij.supabase.co',  # Pooler endpoint
    'database': 'postgres',
    'user': 'postgres.mxnpfsiyaqqwdcokukij',  # Note: different username format
    'password': 'VXUXqY9Uofg9ujoo',
    'port': 6543,  # Pooler port (not 5432)
    'connect_timeout': 30
}

print("Connection Parameters:")
print(f"  Host: {pooler_conn_params['host']}")
print(f"  Port: {pooler_conn_params['port']}")
print(f"  Database: {pooler_conn_params['database']}")
print(f"  User: {pooler_conn_params['user']}")
print()

print("Testing connection...")
try:
    conn = psycopg2.connect(**pooler_conn_params)
    cursor = conn.cursor()
    
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    
    print("[OK] Connected successfully!")
    print(f"PostgreSQL version: {version[:60]}...")
    print()
    
    # Check existing tables
    print("Checking existing NBA schema...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.schemata 
        WHERE schema_name = 'NBA';
    """)
    schema_exists = cursor.fetchone()[0] > 0
    
    if schema_exists:
        print("[INFO] NBA schema already exists")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"[INFO] Found {len(tables)} existing tables")
        
        if len(tables) > 0:
            print()
            print("Existing tables:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f'SELECT COUNT(*) FROM "NBA"."{table_name}";')
                count = cursor.fetchone()[0]
                print(f"  {table_name:30} ({count:6} rows)")
    else:
        print("[INFO] NBA schema does not exist yet")
    
    conn.close()
    
    print()
    print("=" * 60)
    print("Connection successful! Ready to import.")
    print("=" * 60)
    print()
    print("Next step: Run the import")
    print("  python import_via_pooler.py")
    
except Exception as e:
    print(f"[FAIL] Connection failed: {e}")
    print()
    print("Troubleshooting:")
    print("1. Verify Supabase project is active")
    print("2. Check project settings for connection pooler")
    print("3. Ensure IP is allowed in Supabase network settings")

