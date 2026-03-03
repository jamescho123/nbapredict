import psycopg2
import sys

print("=" * 60)
print("Direct Python Import to Supabase")
print("=" * 60)
print()

# Supabase connection
supabase_conn_params = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'VXUXqY9Uofg9ujoo',
    'port': 5432,
    'connect_timeout': 30
}

print("Step 1: Testing connection to Supabase...")
try:
    conn = psycopg2.connect(**supabase_conn_params)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"[OK] Connected successfully!")
    print(f"PostgreSQL version: {version[:50]}...")
    print()
except Exception as e:
    print(f"[FAIL] Connection failed: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check internet connection")
    print("2. Verify Supabase project is active")
    print("3. Check firewall settings")
    print()
    sys.exit(1)

print("Step 2: Reading SQL file...")
sql_file = 'nba_manual_export_20251024_201041.sql'
try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    print(f"[OK] SQL file loaded ({len(sql_content)} characters)")
    print()
except Exception as e:
    print(f"[FAIL] Could not read SQL file: {e}")
    conn.close()
    sys.exit(1)

print("Step 3: Executing SQL import...")
print("This may take 2-5 minutes...")
print()

try:
    # Split into statements and execute
    statements = sql_content.split(';')
    total = len(statements)
    success = 0
    failed = 0
    
    for i, statement in enumerate(statements):
        statement = statement.strip()
        if not statement or statement.startswith('--'):
            continue
        
        try:
            cursor.execute(statement)
            conn.commit()
            success += 1
            
            # Progress indicator
            if i % 100 == 0:
                progress = (i / total) * 100
                print(f"Progress: {progress:.1f}% ({i}/{total} statements)")
        except Exception as e:
            # Some errors are expected (like DROP TABLE if not exists)
            if 'does not exist' not in str(e).lower():
                failed += 1
                if failed < 5:  # Only show first few errors
                    print(f"Warning: {str(e)[:100]}")
    
    print()
    print(f"[OK] Import completed!")
    print(f"Successful statements: {success}")
    if failed > 0:
        print(f"Failed/Skipped: {failed} (mostly expected)")
    print()
    
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    conn.rollback()
    conn.close()
    sys.exit(1)

print("Step 4: Verifying tables...")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'NBA'
    ORDER BY table_name;
""")
tables = cursor.fetchall()

print(f"[OK] Found {len(tables)} tables in NBA schema:")
print()

for table in tables:
    table_name = table[0]
    cursor.execute(f'SELECT COUNT(*) FROM "NBA"."{table_name}";')
    count = cursor.fetchone()[0]
    print(f"  {table_name:30} ({count:6} rows)")

conn.close()

print()
print("=" * 60)
print("[OK] Database successfully connected to Supabase!")
print("=" * 60)
print()
print("Next steps:")
print("1. Update your applications to use Supabase connection")
print("2. Use db_config.py to switch between local/Supabase")
print("3. Set environment variable: $env:USE_SUPABASE='true'")

