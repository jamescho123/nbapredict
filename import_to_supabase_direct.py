"""
Direct import from local PostgreSQL to Supabase
Run this ONLY when connection test succeeds
"""

import psycopg2
import sys

print("=" * 70)
print("Direct Database Migration to Supabase")
print("=" * 70)
print()

# Configurations
LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

SUPABASE_CONFIG = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'VXUXqY9Uofg9ujoo'
}

# Step 1: Test Supabase connection
print("Step 1: Testing Supabase connection...")
try:
    supabase_conn = psycopg2.connect(**SUPABASE_CONFIG, connect_timeout=10)
    print("[OK] Connected to Supabase!")
    print()
except Exception as e:
    print(f"[FAIL] Cannot connect to Supabase: {e}")
    print()
    print("Connection still blocked. Please use manual upload:")
    print("  Upload files: nba_export_part1, part2, and table files")
    print("  URL: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new")
    sys.exit(1)

# Step 2: Connect to local
print("Step 2: Connecting to local database...")
try:
    local_conn = psycopg2.connect(**LOCAL_CONFIG)
    print("[OK] Connected to local database!")
    print()
except Exception as e:
    print(f"[FAIL] Cannot connect to local: {e}")
    supabase_conn.close()
    sys.exit(1)

# Step 3: Setup Supabase schema
print("Step 3: Setting up Supabase...")
supabase_cursor = supabase_conn.cursor()

# Create schema
try:
    supabase_cursor.execute('CREATE SCHEMA IF NOT EXISTS "NBA";')
    supabase_conn.commit()
    print("[OK] NBA schema created")
except Exception as e:
    print(f"[INFO] Schema: {e}")
    supabase_conn.rollback()

# Enable vector extension
try:
    supabase_cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    supabase_conn.commit()
    print("[OK] Vector extension enabled")
except Exception as e:
    print(f"[INFO] Extension: {e}")
    supabase_conn.rollback()

# Create custom types
try:
    supabase_cursor.execute("""
        CREATE TYPE entity_type AS ENUM (
            'player', 'team', 'game', 'injury', 'conflict', 
            'stat', 'penalty', 'trade', 'award', 'location', 'date'
        );
    """)
    supabase_conn.commit()
    print("[OK] Custom types created")
except Exception as e:
    print(f"[INFO] Types: {e}")
    supabase_conn.rollback()

print()

# Step 4: Get tables from local
print("Step 4: Reading tables from local database...")
local_cursor = local_conn.cursor()
local_cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'NBA'
    ORDER BY table_name;
""")
tables = [row[0] for row in local_cursor.fetchall()]
print(f"[OK] Found {len(tables)} tables to migrate")
print()

# Step 5: Migrate tables
print("Step 5: Migrating tables...")
print()

successful = 0
failed = 0

for i, table in enumerate(tables, 1):
    print(f"[{i}/{len(tables)}] {table:30} ", end="", flush=True)
    
    try:
        # Get table structure
        local_cursor.execute(f"""
            SELECT column_name, data_type, udt_name, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'NBA' AND table_name = '{table}'
            ORDER BY ordinal_position;
        """)
        columns = local_cursor.fetchall()
        
        # Build CREATE TABLE
        col_defs = []
        for col_name, data_type, udt_name, is_nullable in columns:
            col_type = udt_name if data_type == 'USER-DEFINED' else data_type
            nullable = '' if is_nullable == 'YES' else ' NOT NULL'
            col_defs.append(f'"{col_name}" {col_type}{nullable}')
        
        create_sql = f'DROP TABLE IF EXISTS "NBA"."{table}" CASCADE; '
        create_sql += f'CREATE TABLE "NBA"."{table}" ({", ".join(col_defs)});'
        
        supabase_cursor.execute(create_sql)
        supabase_conn.commit()
        
        # Copy data
        local_cursor.execute(f'SELECT * FROM "NBA"."{table}";')
        rows = local_cursor.fetchall()
        
        if rows:
            col_names = [desc[0] for desc in local_cursor.description]
            placeholders = ','.join(['%s'] * len(col_names))
            col_names_quoted = ','.join([f'"{c}"' for c in col_names])
            insert_sql = f'INSERT INTO "NBA"."{table}" ({col_names_quoted}) VALUES ({placeholders});'
            
            # Insert in batches for large tables
            batch_size = 1000
            for j in range(0, len(rows), batch_size):
                batch = rows[j:j+batch_size]
                supabase_cursor.executemany(insert_sql, batch)
                supabase_conn.commit()
            
            print(f"[OK] {len(rows):6} rows")
            successful += 1
        else:
            print(f"[OK]      0 rows")
            successful += 1
            
    except Exception as e:
        print(f"[FAIL] {str(e)[:40]}")
        supabase_conn.rollback()
        failed += 1

# Close connections
local_conn.close()
supabase_conn.close()

print()
print("=" * 70)
print("Migration Summary")
print("=" * 70)
print(f"Successful: {successful}/{len(tables)}")
print(f"Failed: {failed}/{len(tables)}")
print()

if failed == 0:
    print("[SUCCESS] All tables migrated successfully!")
    print()
    print("Your database is now connected to Supabase!")
    print()
    print("Update your applications to use Supabase:")
    print("  Use db_config.py with USE_SUPABASE=true")
else:
    print("[WARNING] Some tables failed to migrate")
    print("Check errors above for details")

print()
print("Supabase Dashboard:")
print("https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij")

