import psycopg2

# Check local database
local_conn = psycopg2.connect(
    host='localhost',
    database='James',
    user='postgres',
    password='jcjc1749'
)

cursor = local_conn.cursor()
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'NBA'
    ORDER BY table_name;
""")
local_tables = [row[0] for row in cursor.fetchall()]

print("=== LOCAL DATABASE TABLES ===")
print(f"Total: {len(local_tables)} tables\n")
for i, table in enumerate(local_tables, 1):
    cursor.execute(f'SELECT COUNT(*) FROM "NBA"."{table}";')
    count = cursor.fetchone()[0]
    print(f"{i:2}. {table:30} ({count:6} rows)")

local_conn.close()

# Check exported SQL file
print("\n=== EXPORTED SQL FILE ===")
print("File: nba_manual_export_20251024_201041.sql")

try:
    with open('nba_manual_export_20251024_201041.sql', 'r', encoding='utf-8') as f:
        content = f.read()
        exported_tables = []
        for table in local_tables:
            if f'CREATE TABLE "NBA"."{table}"' in content:
                exported_tables.append(table)
        
        print(f"Tables exported: {len(exported_tables)}/{len(local_tables)}")
        
        if len(exported_tables) == len(local_tables):
            print("[OK] All tables exported successfully!")
        else:
            missing = set(local_tables) - set(exported_tables)
            print(f"[WARNING] Missing tables: {missing}")
except FileNotFoundError:
    print("[ERROR] Export file not found!")

print("\n=== SUPABASE STATUS ===")
print("Status: NOT YET UPLOADED")
print("\nThe SQL file has been generated but needs to be uploaded to Supabase:")
print("1. Open: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new")
print("2. Copy contents of nba_manual_export_20251024_201041.sql")
print("3. Paste and execute in Supabase SQL Editor")
print("\nOr run: python verify_supabase_migration.py (after uploading)")

