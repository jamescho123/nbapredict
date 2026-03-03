import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Local PostgreSQL connection
local_conn_params = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

# Supabase PostgreSQL connection (you need to get these from Supabase dashboard)
# Go to: Project Settings > Database > Connection string (Direct connection)
supabase_conn_params = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'VXUXqY9Uofg9ujoo',
    'port': 5432
}

def get_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'NBA'
        ORDER BY table_name;
    """)
    return [row[0] for row in cursor.fetchall()]

def get_create_schema_sql(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 'CREATE SCHEMA IF NOT EXISTS "NBA";'
    """)
    return cursor.fetchone()[0]

def get_table_ddl(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT 
            'CREATE TABLE IF NOT EXISTS "NBA"."{table_name}" (' ||
            string_agg(
                '"' || column_name || '" ' || 
                CASE 
                    WHEN data_type = 'USER-DEFINED' THEN udt_name
                    WHEN data_type = 'character varying' THEN 'varchar(' || character_maximum_length || ')'
                    WHEN data_type = 'character' THEN 'char(' || character_maximum_length || ')'
                    WHEN data_type = 'numeric' THEN 'numeric(' || numeric_precision || ',' || numeric_scale || ')'
                    ELSE data_type
                END ||
                CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
                ', '
            ) || ');'
        FROM information_schema.columns
        WHERE table_schema = 'NBA' AND table_name = '{table_name}'
        GROUP BY table_name;
    """)
    result = cursor.fetchone()
    return result[0] if result else None

def migrate_data(local_conn, supabase_conn):
    local_cursor = local_conn.cursor()
    supabase_cursor = supabase_conn.cursor()
    
    # Enable pgvector extension on Supabase
    try:
        supabase_cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        supabase_conn.commit()
    except Exception as e:
        print(f"Extension creation: {e}")
        supabase_conn.rollback()
    
    # Create schema
    supabase_cursor.execute('CREATE SCHEMA IF NOT EXISTS "NBA";')
    supabase_conn.commit()
    
    # Get all tables
    tables = get_tables(local_conn)
    
    for table in tables:
        print(f"Migrating {table}...")
        
        # Get table structure
        local_cursor.execute(f"""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = 'NBA' AND table_name = '{table}'
            ORDER BY ordinal_position;
        """)
        columns = local_cursor.fetchall()
        
        # Build CREATE TABLE statement
        col_defs = []
        for col_name, data_type, udt_name in columns:
            if data_type == 'USER-DEFINED':
                col_defs.append(f'"{col_name}" {udt_name}')
            else:
                col_defs.append(f'"{col_name}" {data_type}')
        
        create_table_sql = f'CREATE TABLE IF NOT EXISTS "NBA"."{table}" ({", ".join(col_defs)});'
        
        try:
            supabase_cursor.execute(create_table_sql)
            supabase_conn.commit()
        except Exception as e:
            print(f"Create table {table}: {e}")
            supabase_conn.rollback()
            continue
        
        # Copy data
        local_cursor.execute(f'SELECT * FROM "NBA"."{table}";')
        rows = local_cursor.fetchall()
        
        if rows:
            col_names = [desc[0] for desc in local_cursor.description]
            placeholders = ','.join(['%s'] * len(col_names))
            col_names_quoted = ','.join([f'"{c}"' for c in col_names])
            insert_sql = f'INSERT INTO "NBA"."{table}" ({col_names_quoted}) VALUES ({placeholders});'
            
            try:
                supabase_cursor.executemany(insert_sql, rows)
                supabase_conn.commit()
                print(f"  Migrated {len(rows)} rows")
            except Exception as e:
                print(f"  Data migration error: {e}")
                supabase_conn.rollback()

def main():
    print("Connecting to databases...")
    local_conn = psycopg2.connect(**local_conn_params)
    supabase_conn = psycopg2.connect(**supabase_conn_params)
    
    try:
        migrate_data(local_conn, supabase_conn)
        print("Migration complete!")
    finally:
        local_conn.close()
        supabase_conn.close()

if __name__ == "__main__":
    main()

