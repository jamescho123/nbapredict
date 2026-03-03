import psycopg2
import sys
from datetime import datetime, date, time

sys.stdout.reconfigure(encoding='utf-8')

LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def escape_sql_value(value):
    if value is None:
        return 'NULL'
    elif isinstance(value, str):
        return "'" + value.replace("'", "''").replace("\\", "\\\\") + "'"
    elif isinstance(value, bytes):
        return "'\\x" + value.hex() + "'"
    elif isinstance(value, (datetime, date, time)):
        return f"'{value.isoformat()}'"
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        # Quote everything else as string to be safe
        return "'" + str(value).replace("'", "''").replace("\\", "\\\\") + "'"

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
    
    output_file.write(f"\n-- ============================================================\n")
    output_file.write(f"-- Table: {table_name} ({count} rows)\n")
    output_file.write(f"-- ============================================================\n\n")
    output_file.write(f'TRUNCATE TABLE "{DB_SCHEMA}"."{table_name}" CASCADE;\n\n')
    
    column_list = ', '.join([f'"{col}"' for col in column_names])
    cursor.execute(f'SELECT {column_list} FROM "{DB_SCHEMA}"."{table_name}"')
    
    batch_size = 100
    inserted = 0
    batch = []
    
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        
        for row in rows:
            batch.append(row)
        
        if len(batch) >= batch_size:
            values_list = []
            for row in batch:
                values = ', '.join([escape_sql_value(val) for val in row])
                values_list.append(f'({values})')
            
            output_file.write(f'INSERT INTO "{DB_SCHEMA}"."{table_name}" ({column_list}) VALUES\n')
            output_file.write(',\n'.join(values_list))
            output_file.write(';\n\n')
            
            inserted += len(batch)
            batch = []
            if inserted % 1000 == 0:
                print(f"    Progress: {inserted}/{count} rows ({inserted*100//count}%)")
    
    if batch:
        values_list = []
        for row in batch:
            values = ', '.join([escape_sql_value(val) for val in row])
            values_list.append(f'({values})')
        
        output_file.write(f'INSERT INTO "{DB_SCHEMA}"."{table_name}" ({column_list}) VALUES\n')
        output_file.write(',\n'.join(values_list))
        output_file.write(';\n\n')
        
        inserted += len(batch)
    
    print(f"    ✓ Exported {inserted} rows")
    return inserted

def main():
    print("="*60)
    print("Export Local Database to SQL for pgAdmin Import")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("Connecting to Local PostgreSQL...")
    try:
        conn = psycopg2.connect(**LOCAL_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected to Local PostgreSQL\n")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return
    
    print("Fetching table list...")
    cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{DB_SCHEMA}'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(tables)} tables: {', '.join(tables)}\n")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'nba_export_for_pgadmin_{timestamp}.sql'
    
    print(f"Creating export file: {filename}")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"-- NBA Database Export for pgAdmin Import\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Schema: {DB_SCHEMA}\n")
        f.write(f"-- Tables: {len(tables)}\n")
        f.write(f"--\n")
        f.write(f"-- Instructions:\n")
        f.write(f"-- 1. Connect pgAdmin to Supabase\n")
        f.write(f"-- 2. Open Query Tool on 'postgres' database\n")
        f.write(f"-- 3. Load this file and execute (F5)\n")
        f.write(f"--\n\n")
        
        f.write(f'-- Ensure NBA schema exists\n')
        f.write(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}";\n\n')
        
        total_rows = 0
        for i, table in enumerate(tables, 1):
            print(f"[{i}/{len(tables)}] {table}")
            rows = export_table_to_sql(cursor, table, f)
            total_rows += rows
        
        f.write(f"\n-- Export complete: {total_rows} total rows\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("EXPORT COMPLETE")
    print("="*60)
    print(f"File: {filename}")
    print(f"Total rows: {total_rows}")
    print(f"\nNext steps:")
    print(f"1. Open pgAdmin 4")
    print(f"2. Connect to Supabase server")
    print(f"3. Right-click 'postgres' database → Query Tool")
    print(f"4. File → Open File → Select: {filename}")
    print(f"5. Execute (F5)")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

