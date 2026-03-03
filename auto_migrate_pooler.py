import psycopg2
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

# Try connection pooler instead of direct connection
SUPABASE_POOLER_CONFIG = {
    'host': 'mxnpfsiyaqqwdcokukij.supabase.co',
    'database': 'postgres',
    'user': 'postgres.mxnpfsiyaqqwdcokukij',
    'password': 'VXUXqY9Uofg9ujoo',
    'port': 6543
}

SUPABASE_DIRECT_CONFIG = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'VXUXqY9Uofg9ujoo',
    'port': 5432
}

DB_SCHEMA = 'NBA'

def test_connections():
    print("Testing database connections...")
    print("-" * 60)
    
    print("1. Testing Local PostgreSQL...")
    try:
        local_conn = psycopg2.connect(**LOCAL_CONFIG)
        local_conn.close()
        print("   ✓ Local PostgreSQL connected")
    except Exception as e:
        print(f"   ✗ Local PostgreSQL failed: {e}")
        return False, None
    
    print("\n2. Testing Supabase Connection Pooler...")
    try:
        supabase_conn = psycopg2.connect(**SUPABASE_POOLER_CONFIG, connect_timeout=15)
        cursor = supabase_conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"   ✓ Supabase Pooler connected")
        print(f"   PostgreSQL: {version[:50]}...")
        cursor.close()
        supabase_conn.close()
        return True, SUPABASE_POOLER_CONFIG
    except Exception as e:
        print(f"   ✗ Supabase Pooler failed: {e}")
    
    print("\n3. Testing Supabase Direct Connection...")
    try:
        supabase_conn = psycopg2.connect(**SUPABASE_DIRECT_CONFIG, connect_timeout=15)
        cursor = supabase_conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"   ✓ Supabase Direct connected")
        print(f"   PostgreSQL: {version[:50]}...")
        cursor.close()
        supabase_conn.close()
        return True, SUPABASE_DIRECT_CONFIG
    except Exception as e:
        print(f"   ✗ Supabase Direct failed: {e}")
    
    print("\n   Network connectivity issue detected.")
    print("   Please use manual SQL upload method:")
    print("   See: UPLOAD_TO_SUPABASE.md")
    return False, None

def migrate_table(table_name, supabase_config, batch_size=1000):
    print(f"\nMigrating: {table_name}")
    print("-" * 60)
    
    local_conn = psycopg2.connect(**LOCAL_CONFIG)
    supabase_conn = psycopg2.connect(**supabase_config)
    
    local_cursor = local_conn.cursor()
    supabase_cursor = supabase_conn.cursor()
    
    try:
        local_cursor.execute(f"""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_schema = '{DB_SCHEMA}' 
            AND table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in local_cursor.fetchall()]
        column_list = ', '.join([f'"{col}"' for col in columns])
        
        local_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
        local_count = local_cursor.fetchone()[0]
        print(f"Local rows: {local_count}")
        
        if local_count == 0:
            print("Skipped (no data)")
            return {"status": "skipped", "rows": 0}
        
        print("Truncating Supabase table...")
        supabase_cursor.execute(f'TRUNCATE TABLE "{DB_SCHEMA}"."{table_name}" CASCADE')
        supabase_conn.commit()
        
        print("Copying data...")
        local_cursor.execute(f'SELECT {column_list} FROM "{DB_SCHEMA}"."{table_name}"')
        
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f'INSERT INTO "{DB_SCHEMA}"."{table_name}" ({column_list}) VALUES ({placeholders})'
        
        inserted = 0
        batch = []
        
        while True:
            rows = local_cursor.fetchmany(batch_size)
            if not rows:
                break
            
            batch.extend(rows)
            
            if len(batch) >= batch_size:
                supabase_cursor.executemany(insert_query, batch)
                supabase_conn.commit()
                inserted += len(batch)
                print(f"  Progress: {inserted}/{local_count} rows ({inserted*100//local_count}%)")
                batch = []
        
        if batch:
            supabase_cursor.executemany(insert_query, batch)
            supabase_conn.commit()
            inserted += len(batch)
        
        supabase_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
        supabase_count = supabase_cursor.fetchone()[0]
        
        verified = local_count == supabase_count
        print(f"✓ Complete: {inserted} rows migrated")
        print(f"Verification: Local={local_count}, Supabase={supabase_count}, Match={verified}")
        
        return {
            "status": "success",
            "local_count": local_count,
            "inserted": inserted,
            "supabase_count": supabase_count,
            "verified": verified
        }
        
    except Exception as e:
        print(f"✗ Error: {e}")
        supabase_conn.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        local_cursor.close()
        supabase_cursor.close()
        local_conn.close()
        supabase_conn.close()

def migrate_all_tables():
    print("=" * 60)
    print("NBA Database Automatic Migration")
    print("Local PostgreSQL → Supabase")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    connected, supabase_config = test_connections()
    if not connected:
        return
    
    print("\n" + "=" * 60)
    print("Starting Migration")
    print("=" * 60)
    
    local_conn = psycopg2.connect(**LOCAL_CONFIG)
    cursor = local_conn.cursor()
    
    cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{DB_SCHEMA}'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    local_conn.close()
    
    print(f"Found {len(tables)} tables to migrate\n")
    
    results = {}
    for i, table in enumerate(tables, 1):
        print(f"\n[{i}/{len(tables)}] {table}")
        result = migrate_table(table, supabase_config)
        results[table] = result
    
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    
    successful = 0
    failed = 0
    skipped = 0
    total_rows = 0
    
    for table, result in results.items():
        status = result.get("status")
        if status == "success":
            successful += 1
            total_rows += result.get("inserted", 0)
            verified = "✓" if result.get("verified") else "⚠"
            print(f"{verified} {table}: {result.get('inserted')} rows")
        elif status == "error":
            failed += 1
            print(f"✗ {table}: {result.get('error')}")
        elif status == "skipped":
            skipped += 1
            print(f"- {table}: skipped")
    
    print(f"\nTables: {len(tables)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Total rows: {total_rows}")
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'auto_migration_report_{timestamp}.json'
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nReport saved: {report_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        print(f"Migrating single table: {table_name}\n")
        connected, supabase_config = test_connections()
        if connected:
            migrate_table(table_name, supabase_config)
    else:
        migrate_all_tables()

