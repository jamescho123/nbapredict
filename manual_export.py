import psycopg2
from datetime import datetime

local_conn_params = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

def export_schema():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"nba_manual_export_{timestamp}.sql"
    
    print(f"Connecting to local database...")
    conn = psycopg2.connect(**local_conn_params)
    cursor = conn.cursor()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("-- NBA Database Export\n")
        f.write(f"-- Generated: {datetime.now()}\n\n")
        
        # Create schema
        f.write('CREATE SCHEMA IF NOT EXISTS "NBA";\n\n')
        
        # Enable vector extension
        f.write("CREATE EXTENSION IF NOT EXISTS vector;\n\n")
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            print(f"Exporting {table}...")
            
            # Get columns
            cursor.execute(f"""
                SELECT column_name, data_type, udt_name, is_nullable,
                       character_maximum_length, numeric_precision, numeric_scale
                FROM information_schema.columns
                WHERE table_schema = 'NBA' AND table_name = '{table}'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            # CREATE TABLE
            f.write(f'-- Table: {table}\n')
            f.write(f'DROP TABLE IF EXISTS "NBA"."{table}" CASCADE;\n')
            f.write(f'CREATE TABLE "NBA"."{table}" (\n')
            
            col_defs = []
            for col_name, data_type, udt_name, is_nullable, char_len, num_prec, num_scale in columns:
                if data_type == 'USER-DEFINED':
                    col_type = udt_name
                elif data_type == 'character varying' and char_len:
                    col_type = f'varchar({char_len})'
                elif data_type == 'numeric' and num_prec and num_scale:
                    col_type = f'numeric({num_prec},{num_scale})'
                else:
                    col_type = data_type
                
                nullable = '' if is_nullable == 'YES' else ' NOT NULL'
                col_defs.append(f'  "{col_name}" {col_type}{nullable}')
            
            f.write(',\n'.join(col_defs))
            f.write('\n);\n\n')
            
            # Get data
            cursor.execute(f'SELECT * FROM "NBA"."{table}";')
            rows = cursor.fetchall()
            
            if rows:
                col_names = [desc[0] for desc in cursor.description]
                col_names_str = ', '.join([f'"{c}"' for c in col_names])
                
                f.write(f'-- Data for {table}\n')
                for row in rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            # Escape single quotes
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            # For other types (datetime, etc)
                            values.append(f"'{str(val)}'")
                    
                    values_str = ', '.join(values)
                    f.write(f'INSERT INTO "NBA"."{table}" ({col_names_str}) VALUES ({values_str});\n')
                
                f.write(f'\n-- {len(rows)} rows inserted\n\n')
        
        # Get constraints
        f.write("-- Constraints and indexes will need to be recreated manually\n")
    
    conn.close()
    
    print(f"\n[OK] Export complete: {output_file}")
    print(f"\nUpload to Supabase:")
    print(f"1. Open: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new")
    print(f"2. Copy contents of {output_file}")
    print(f"3. Paste and execute")

if __name__ == "__main__":
    export_schema()

