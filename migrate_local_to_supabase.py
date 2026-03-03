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

def get_all_tables(conn):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{DB_SCHEMA}'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables

def get_table_columns(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns 
        WHERE table_schema = '{DB_SCHEMA}' 
        AND table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    cursor.close()
    return columns

def get_row_count(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
    count = cursor.fetchone()[0]
    cursor.close()
    return count

def copy_table_data(local_conn, supabase_conn, table_name, batch_size=1000):
    print(f"\n{'='*60}")
    print(f"Processing table: {table_name}")
    print(f"{'='*60}")
    
    local_cursor = local_conn.cursor()
    supabase_cursor = supabase_conn.cursor()
    
    try:
        local_count = get_row_count(local_conn, table_name)
        print(f"Local rows: {local_count}")
        
        if local_count == 0:
            print("No data to copy")
            return {"status": "skipped", "rows": 0}
        
        columns = get_table_columns(local_conn, table_name)
        column_names = [col[0] for col in columns]
        column_list = ', '.join([f'"{col}"' for col in column_names])
        placeholders = ', '.join(['%s'] * len(column_names))
        
        print(f"Columns: {len(column_names)}")
        
        print("Truncating Supabase table...")
        supabase_cursor.execute(f'TRUNCATE TABLE "{DB_SCHEMA}"."{table_name}" CASCADE')
        supabase_conn.commit()
        
        print("Fetching data from local database...")
        local_cursor.execute(f'SELECT {column_list} FROM "{DB_SCHEMA}"."{table_name}"')
        
        inserted = 0
        batch = []
        
        while True:
            rows = local_cursor.fetchmany(batch_size)
            if not rows:
                break
            
            batch.extend(rows)
            
            if len(batch) >= batch_size:
                insert_query = f'INSERT INTO "{DB_SCHEMA}"."{table_name}" ({column_list}) VALUES ({placeholders})'
                supabase_cursor.executemany(insert_query, batch)
                supabase_conn.commit()
                inserted += len(batch)
                print(f"Progress: {inserted}/{local_count} rows inserted ({inserted*100//local_count}%)")
                batch = []
        
        if batch:
            insert_query = f'INSERT INTO "{DB_SCHEMA}"."{table_name}" ({column_list}) VALUES ({placeholders})'
            supabase_cursor.executemany(insert_query, batch)
            supabase_conn.commit()
            inserted += len(batch)
        
        supabase_count = get_row_count(supabase_conn, table_name)
        print(f"✓ Complete: {inserted} rows inserted")
        print(f"Verification: Local={local_count}, Supabase={supabase_count}")
        
        return {
            "status": "success",
            "local_count": local_count,
            "inserted": inserted,
            "supabase_count": supabase_count,
            "match": local_count == supabase_count
        }
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        supabase_conn.rollback()
        return {"status": "error", "error": str(e)}
        
    finally:
        local_cursor.close()
        supabase_cursor.close()

def main():
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
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        local_conn.close()
        return
    
    print("\nFetching table list...")
    tables = get_all_tables(local_conn)
    print(f"Found {len(tables)} tables: {', '.join(tables)}")
    
    results = {}
    
    for i, table in enumerate(tables, 1):
        print(f"\n[{i}/{len(tables)}] Migrating table: {table}")
        result = copy_table_data(local_conn, supabase_conn, table)
        results[table] = result
    
    local_conn.close()
    supabase_conn.close()
    
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    
    successful = 0
    failed = 0
    skipped = 0
    total_rows = 0
    
    for table, result in results.items():
        status = result.get("status")
        if status == "success":
            successful += 1
            total_rows += result.get("inserted", 0)
            match_icon = "✓" if result.get("match") else "⚠"
            print(f"{match_icon} {table}: {result.get('inserted')} rows")
        elif status == "error":
            failed += 1
            print(f"✗ {table}: {result.get('error')}")
        elif status == "skipped":
            skipped += 1
            print(f"- {table}: skipped (no data)")
    
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
    main()

