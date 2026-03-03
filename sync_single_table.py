import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

SUPABASE_CONFIG = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'VXUXqY9Uofg9ujoo',
    'port': 5432
}

DB_SCHEMA = 'NBA'

def sync_table(table_name):
    print(f"Syncing table: {table_name}")
    
    local_conn = psycopg2.connect(**LOCAL_CONFIG)
    supabase_conn = psycopg2.connect(**SUPABASE_CONFIG)
    
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
        
        print("Truncating Supabase table...")
        supabase_cursor.execute(f'TRUNCATE TABLE "{DB_SCHEMA}"."{table_name}" CASCADE')
        supabase_conn.commit()
        
        print("Copying data...")
        local_cursor.execute(f'SELECT {column_list} FROM "{DB_SCHEMA}"."{table_name}"')
        
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f'INSERT INTO "{DB_SCHEMA}"."{table_name}" ({column_list}) VALUES ({placeholders})'
        
        batch_size = 1000
        inserted = 0
        
        while True:
            rows = local_cursor.fetchmany(batch_size)
            if not rows:
                break
            
            supabase_cursor.executemany(insert_query, rows)
            supabase_conn.commit()
            inserted += len(rows)
            print(f"Progress: {inserted}/{local_count} rows")
        
        supabase_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
        supabase_count = supabase_cursor.fetchone()[0]
        
        print(f"\n✓ Sync complete!")
        print(f"Local: {local_count} rows")
        print(f"Supabase: {supabase_count} rows")
        print(f"Match: {local_count == supabase_count}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        supabase_conn.rollback()
    finally:
        local_cursor.close()
        supabase_cursor.close()
        local_conn.close()
        supabase_conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sync_single_table.py <table_name>")
        print("Example: python sync_single_table.py Teams")
        sys.exit(1)
    
    table_name = sys.argv[1]
    sync_table(table_name)

