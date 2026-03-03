import psycopg2
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def export_table_to_sql(cursor, table_name, output_file):
    cursor.execute(f"""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns 
        WHERE table_schema = '{DB_SCHEMA}' 
        AND table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    column_names = [col[0] for col in columns]
    
    cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print(f"  Skipping {table_name} (no data)")
        return 0
    
    print(f"  Exporting {table_name} ({count} rows)...")
    
    output_file.write(f"\n-- Table: {table_name} ({count} rows)\n")
    output_file.write(f'TRUNCATE TABLE "{DB_SCHEMA}"."{table_name}" CASCADE;\n\n')
    
    column_list = ', '.join([f'"{col}"' for col in column_names])
    cursor.execute(f'SELECT {column_list} FROM "{DB_SCHEMA}"."{table_name}"')
    
    batch_size = 100
    inserted = 0
    
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        
        for row in rows:
            values = []
            for i, val in enumerate(row):
                if val is None:
                    values.append('NULL')
                elif isinstance(val, str):
                    escaped = val.replace("'", "''").replace("\\", "\\\\")
                    values.append(f"'{escaped}'")
                elif isinstance(val, (list, dict)):
                    import json
                    escaped = json.dumps(val).replace("'", "''")
                    values.append(f"'{escaped}'")
                elif isinstance(val, bytes):
                    values.append(f"'\\x{val.hex()}'")
                else:
                    values.append(str(val))
            
            values_str = ', '.join(values)
            output_file.write(f'INSERT INTO "{DB_SCHEMA}"."{table_name}" ({column_list}) VALUES ({values_str});\n')
            inserted += 1
        
        if inserted % 1000 == 0:
            print(f"    Progress: {inserted}/{count} rows")
    
    output_file.write('\n')
    print(f"  ✓ Exported {inserted} rows")
    return inserted

def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'nba_full_export_{timestamp}.sql'
    
    print("="*60)
    print("NBA Database SQL Export")
    print("="*60)
    print(f"Output file: {output_filename}")
    
    print("\nConnecting to Local PostgreSQL...")
    conn = psycopg2.connect(**LOCAL_CONFIG)
    cursor = conn.cursor()
    print("✓ Connected")
    
    print("\nFetching table list...")
    cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{DB_SCHEMA}'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(tables)} tables: {', '.join(tables)}")
    
    print("\nExporting tables...")
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(f"-- NBA Database Export\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Schema: {DB_SCHEMA}\n")
        f.write(f"-- Tables: {len(tables)}\n\n")
        f.write(f"SET search_path TO \"{DB_SCHEMA}\";\n\n")
        
        total_rows = 0
        for i, table in enumerate(tables, 1):
            print(f"[{i}/{len(tables)}] Processing {table}")
            rows_exported = export_table_to_sql(cursor, table, f)
            total_rows += rows_exported
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("EXPORT COMPLETE")
    print("="*60)
    print(f"Tables exported: {len(tables)}")
    print(f"Total rows: {total_rows}")
    print(f"Output file: {output_filename}")
    print("\nNext steps:")
    print("1. Open Supabase SQL Editor:")
    print("   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new")
    print(f"2. Copy contents of {output_filename}")
    print("3. Paste into SQL Editor and execute")
    print("\nNote: For large files, you may need to execute in batches")

if __name__ == "__main__":
    main()

