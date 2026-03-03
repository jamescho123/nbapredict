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

SUPABASE_CONFIG = {
    'host': 'aws-1-ap-southeast-1.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.mxnpfsiyaqqwdcokukij',
    'password': 'Jcjc1749!!!!',
    'port': 5432
}

DB_SCHEMA = 'NBA'

def migrate_table(table_name, truncate=True, batch_size=1000):
    print(f"\n{'='*60}")
    print(f"Migrating table: {table_name}")
    print(f"{'='*60}")
    
    local_conn = psycopg2.connect(**LOCAL_CONFIG)
    local_cursor = local_conn.cursor()
    
    supabase_conn = psycopg2.connect(**SUPABASE_CONFIG)
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
        
        if not columns:
            raise ValueError(f"Table {table_name} not found in local database")
        
        column_list = ', '.join([f'"{col}"' for col in columns])
        
        local_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
        local_count = local_cursor.fetchone()[0]
        print(f"Local rows: {local_count}")
        
        if truncate:
            print("Truncating Supabase table...")
            supabase_cursor.execute(f'TRUNCATE TABLE "{DB_SCHEMA}"."{table_name}" CASCADE')
            supabase_conn.commit()
        
        if local_count == 0:
            result = {
                "table": table_name,
                "status": "skipped",
                "message": "No data to migrate",
                "rows_migrated": 0
            }
            print("No data to migrate")
            return result
        
        print("Fetching data from local database...")
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
                print(f"Progress: {inserted}/{local_count} rows ({inserted*100//local_count}%)")
                batch = []
        
        if batch:
            supabase_cursor.executemany(insert_query, batch)
            supabase_conn.commit()
            inserted += len(batch)
        
        supabase_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
        supabase_count = supabase_cursor.fetchone()[0]
        
        result = {
            "table": table_name,
            "status": "success",
            "local_count": local_count,
            "rows_migrated": inserted,
            "supabase_count": supabase_count,
            "verified": local_count == supabase_count
        }
        
        print(f"✓ Complete: {inserted} rows migrated")
        print(f"Verification: Local={local_count}, Supabase={supabase_count}")
        return result
        
    except Exception as e:
        supabase_conn.rollback()
        result = {
            "table": table_name,
            "status": "error",
            "error": str(e)
        }
        print(f"✗ Error: {str(e)}")
        return result
    finally:
        local_cursor.close()
        local_conn.close()
        supabase_cursor.close()
        supabase_conn.close()

def migrate_all_tables(batch_size=1000):
    print("="*60)
    print("NBA Database Migration: Local PostgreSQL → Supabase")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nConnecting to Local PostgreSQL...")
    try:
        local_conn = psycopg2.connect(**LOCAL_CONFIG)
        print("✓ Connected to Local PostgreSQL")
    except Exception as e:
        print(f"✗ Failed to connect to Local PostgreSQL: {e}")
        return
    
    print("\nConnecting to Supabase...")
    try:
        supabase_conn = psycopg2.connect(**SUPABASE_CONFIG)
        print("✓ Connected to Supabase")
        supabase_conn.close()
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        print("\nNetwork connectivity issue detected.")
        print("Please check:")
        print("  1. Internet connection")
        print("  2. VPN if required")
        print("  3. Firewall settings")
        local_conn.close()
        return
    
    local_conn.close()
    
    print("\nFetching table list...")
    local_conn = psycopg2.connect(**LOCAL_CONFIG)
    local_cursor = local_conn.cursor()
    
    local_cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{DB_SCHEMA}'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in local_cursor.fetchall()]
    local_cursor.close()
    local_conn.close()
    
    print(f"Found {len(tables)} tables: {', '.join(tables)}")
    
    results = {}
    total_rows = 0
    
    for i, table in enumerate(tables, 1):
        print(f"\n[{i}/{len(tables)}] Processing: {table}")
        result = migrate_table(table, truncate=True, batch_size=batch_size)
        results[table] = result
        
        if result.get("status") == "success":
            total_rows += result.get("rows_migrated", 0)
    
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    
    successful = 0
    failed = 0
    skipped = 0
    
    for table, result in results.items():
        status = result.get("status")
        if status == "success":
            successful += 1
            verified = "✓" if result.get("verified") else "⚠"
            print(f"{verified} {table}: {result.get('rows_migrated')} rows")
        elif status == "error":
            failed += 1
            print(f"✗ {table}: {result.get('error')}")
        elif status == "skipped":
            skipped += 1
            print(f"- {table}: skipped")
    
    print(f"\nTables processed: {len(tables)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Total rows migrated: {total_rows}")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    migrate_all_tables()



