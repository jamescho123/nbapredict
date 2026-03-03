import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_CONFIG = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'VXUXqY9Uofg9ujoo',
    'port': 5432
}

DB_SCHEMA = 'NBA'

def check_supabase_data():
    print("Connecting to Supabase...")
    try:
        conn = psycopg2.connect(**SUPABASE_CONFIG)
        print("✓ Connected to Supabase\n")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("\nThis script requires network access to Supabase.")
        print("If blocked, verify data directly in Supabase SQL Editor.")
        return
    
    cursor = conn.cursor()
    
    print("Checking tables in Supabase:")
    print("="*60)
    
    cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{DB_SCHEMA}'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"{'Table':<30} {'Rows':<15} {'Status'}")
    print("-"*60)
    
    expected = {
        'Matches': 1179,
        'News': 7293,
        'Players': 50,
        'Schedule': 308,
        'Season2024_25_News': 763,
        'Season2024_25_Results': 24,
        'Season2024_25_Schedule': 24,
        'TeamPlayer': 11603,
        'Teams': 85,
        'Test2024_25': 2,
        'VectorNews': 3594,
        'entity': 11,
        'entity_mention': 14,
        'news': 3
    }
    
    total_rows = 0
    matches = 0
    
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table}"')
            count = cursor.fetchone()[0]
            total_rows += count
            
            if table in expected:
                if count == expected[table]:
                    status = "✓ Match"
                    matches += 1
                else:
                    status = f"⚠ Expected {expected[table]}"
            else:
                status = "- No data expected"
            
            print(f"{table:<30} {count:<15} {status}")
        except Exception as e:
            print(f"{table:<30} {'ERROR':<15} ✗ {str(e)[:20]}")
    
    print("="*60)
    print(f"Total rows in Supabase: {total_rows}")
    print(f"Expected tables with data: {len(expected)}")
    print(f"Tables matching expected: {matches}")
    
    if matches == len(expected):
        print("\n✓ All data uploaded successfully!")
    else:
        print(f"\n⚠ {len(expected) - matches} tables don't match expected counts")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_supabase_data()

