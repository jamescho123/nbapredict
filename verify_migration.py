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

def verify_migration():
    print("Verifying migration between Local and Supabase...")
    
    local_conn = psycopg2.connect(**LOCAL_CONFIG)
    supabase_conn = psycopg2.connect(**SUPABASE_CONFIG)
    
    local_cursor = local_conn.cursor()
    supabase_cursor = supabase_conn.cursor()
    
    local_cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{DB_SCHEMA}'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in local_cursor.fetchall()]
    
    print(f"\nComparing {len(tables)} tables:\n")
    print(f"{'Table':<30} {'Local':<15} {'Supabase':<15} {'Status'}")
    print("="*70)
    
    all_match = True
    
    for table in tables:
        try:
            local_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table}"')
            local_count = local_cursor.fetchone()[0]
            
            supabase_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table}"')
            supabase_count = supabase_cursor.fetchone()[0]
            
            status = "✓ Match" if local_count == supabase_count else "✗ Mismatch"
            if local_count != supabase_count:
                all_match = False
            
            print(f"{table:<30} {local_count:<15} {supabase_count:<15} {status}")
        except Exception as e:
            print(f"{table:<30} {'ERROR':<15} {'ERROR':<15} ✗ {str(e)[:20]}")
            all_match = False
    
    print("="*70)
    
    if all_match:
        print("\n✓ All tables match! Migration successful.")
    else:
        print("\n⚠ Some tables don't match. Review the differences above.")
    
    local_cursor.close()
    supabase_cursor.close()
    local_conn.close()
    supabase_conn.close()

if __name__ == "__main__":
    verify_migration()

