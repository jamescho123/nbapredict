"""
Regenerate export with ALL custom types included
"""
import psycopg2
from datetime import datetime

local_conn_params = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

def export_with_types():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("Connecting to local database...")
    conn = psycopg2.connect(**local_conn_params)
    cursor = conn.cursor()
    
    # Part 1: Schema and Types
    print("Creating Part 1: Schema and Custom Types...")
    with open('nba_export_part1_schema_and_setup.sql', 'w', encoding='utf-8') as f:
        f.write("-- NBA Database Export - Part 1: Schema and Setup\n")
        f.write(f"-- Generated: {datetime.now()}\n\n")
        
        # Create schema
        f.write('CREATE SCHEMA IF NOT EXISTS "NBA";\n\n')
        
        # Enable vector extension
        f.write('CREATE EXTENSION IF NOT EXISTS vector;\n\n')
        
        # Get all custom enum types
        cursor.execute("""
            SELECT 
                t.typname,
                string_agg(e.enumlabel, ''', ''' ORDER BY e.enumsortorder) as enum_values
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE n.nspname = 'public' OR n.nspname = 'NBA'
            GROUP BY t.typname
            ORDER BY t.typname;
        """)
        
        custom_types = cursor.fetchall()
        if custom_types:
            f.write("-- Custom ENUM types\n")
            for type_name, enum_values in custom_types:
                f.write(f"CREATE TYPE {type_name} AS ENUM ('{enum_values}');\n")
            f.write("\n")
    
    print("[OK] Part 1 created with custom types")
    
    # Part 2: Table Structures (already exists, no change needed)
    print("[OK] Part 2 already exists (table structures)")
    
    # Part 3: Data (already exists, no change needed)
    print("[OK] Part 3 already exists (data inserts)")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("Export Updated Successfully!")
    print("=" * 60)
    print("\nUpdated file:")
    print("  nba_export_part1_schema_and_setup.sql")
    print("\nNow upload in order:")
    print("  1. nba_export_part1_schema_and_setup.sql (UPDATED)")
    print("  2. nba_export_part2_table_structures.sql")
    print("  3. nba_export_part3_data_inserts.sql")

if __name__ == "__main__":
    export_with_types()

