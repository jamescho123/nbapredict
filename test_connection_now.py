import psycopg2

print("=" * 60)
print("Testing Supabase Connection (Firewall Closed)")
print("=" * 60)
print()

# Test configurations
configs = [
    {
        'name': 'Direct Connection (Port 5432)',
        'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'VXUXqY9Uofg9ujoo',
    },
    {
        'name': 'Connection Pooler (Port 6543)',
        'host': 'mxnpfsiyaqqwdcokukij.supabase.co',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.mxnpfsiyaqqwdcokukij',
        'password': 'VXUXqY9Uofg9ujoo',
    },
]

connection_works = False
working_config = None

for config in configs:
    name = config.get('name', 'Unknown')
    print(f"Testing: {name}")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print()
    
    # Remove name from config for connection
    test_config = {k: v for k, v in config.items() if k != 'name'}
    
    try:
        conn = psycopg2.connect(**test_config, connect_timeout=10)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print("[SUCCESS] Connected!")
        print(f"PostgreSQL: {version[:60]}...")
        print()
        
        # Check for NBA schema
        cursor.execute("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'NBA';")
        has_nba = cursor.fetchone()[0] > 0
        print(f"NBA schema exists: {has_nba}")
        
        if has_nba:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'NBA' ORDER BY table_name;")
            tables = cursor.fetchall()
            print(f"Tables found: {len(tables)}")
            
            if len(tables) > 0:
                print()
                print("Existing tables:")
                for table in tables:
                    cursor.execute(f'SELECT COUNT(*) FROM "NBA"."{table[0]}";')
                    count = cursor.fetchone()[0]
                    print(f"  {table[0]:30} ({count:6} rows)")
        
        conn.close()
        
        connection_works = True
        working_config = config
        break
        
    except Exception as e:
        print(f"[FAIL] {str(e)[:80]}")
        print()

print()
print("=" * 60)
if connection_works:
    print("SUCCESS! Connection works with firewall closed!")
    print("=" * 60)
    print()
    print("Working configuration:")
    print(f"  Host: {working_config['host']}")
    print(f"  Port: {working_config['port']}")
    print(f"  User: {working_config['user']}")
    print()
    
    if not cursor.execute("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'NBA';") or cursor.fetchone()[0] == 0:
        print("Next step: Run migration")
        print("  python import_to_supabase.py")
    else:
        print("Your database is already connected!")
        print("Check the tables above to see what's already there.")
else:
    print("Connection still failed")
    print("=" * 60)
    print()
    print("Even with firewall closed, connection doesn't work.")
    print("Please use manual upload method:")
    print("  See files starting with nba_export_*")
    print()
    print("Or check:")
    print("1. Antivirus software might still be blocking")
    print("2. Router firewall")
    print("3. ISP restrictions")

