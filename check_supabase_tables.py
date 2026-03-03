import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_CONFIG = {
    'host': 'aws-1-ap-southeast-1.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.mxnpfsiyaqqwdcokukij',
    'password': 'Jcjc1749!!!!',
    'port': 5432
}

DB_SCHEMA = 'NBA'

print("="*60)
print("Checking Supabase Database")
print("="*60)

try:
    conn = psycopg2.connect(**SUPABASE_CONFIG)
    cursor = conn.cursor()
    
    print("\n1. Checking if NBA schema exists...")
    cursor.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name = %s
    """, (DB_SCHEMA,))
    schema_exists = cursor.fetchone()
    
    if schema_exists:
        print(f"   ✓ Schema '{DB_SCHEMA}' exists")
    else:
        print(f"   ✗ Schema '{DB_SCHEMA}' does NOT exist")
        print(f"   Creating schema...")
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"')
        conn.commit()
        print(f"   ✓ Schema '{DB_SCHEMA}' created")
    
    print("\n2. Listing all schemas...")
    cursor.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name
    """)
    schemas = cursor.fetchall()
    print(f"   Found {len(schemas)} schemas:")
    for schema in schemas:
        print(f"     - {schema[0]}")
    
    print(f"\n3. Checking tables in '{DB_SCHEMA}' schema...")
    cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{DB_SCHEMA}'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"   ✓ Found {len(tables)} tables:")
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table[0]}"')
            count = cursor.fetchone()[0]
            print(f"     - {table[0]}: {count} rows")
    else:
        print(f"   ✗ No tables found in '{DB_SCHEMA}' schema")
        print(f"\n   Tables need to be migrated!")
    
    print("\n4. Checking all tables in database (any schema)...")
    cursor.execute("""
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_type = 'BASE TABLE'
        AND table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY table_schema, table_name
    """)
    all_tables = cursor.fetchall()
    print(f"   Found {len(all_tables)} tables total:")
    current_schema = None
    for schema, table in all_tables:
        if schema != current_schema:
            print(f"\n   Schema: {schema}")
            current_schema = schema
        print(f"     - {table}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    if tables:
        print(f"✓ NBA schema exists with {len(tables)} tables")
        print("\nTo view in pgAdmin:")
        print("1. Refresh the database (right-click 'postgres' → Refresh)")
        print("2. Expand: Schemas → NBA → Tables")
    else:
        print("✗ NBA schema exists but has no tables")
        print("\nNext steps:")
        print("1. Import SQL file via pgAdmin Query Tool")
        print("2. Or run: python migrate_local_to_supabase.py")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check connection settings")
    print("2. Verify network connectivity")
    print("3. Check if Supabase project is active")

