import os
os.environ['USE_SUPABASE'] = 'true'

import psycopg2
from db_config import DB_CONFIG, DB_SCHEMA

def connect_supabase():
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=10)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"Connected to Supabase!")
        print(f"PostgreSQL version: {version[:80]}")
        
        cursor.execute(f"SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"Database: {db_info[0]}, User: {db_info[1]}")
        
        cursor.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{DB_SCHEMA}';")
        schema_exists = cursor.fetchone()
        if schema_exists:
            print(f"Schema '{DB_SCHEMA}' exists")
        else:
            print(f"Schema '{DB_SCHEMA}' not found")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Attempting to connect to Supabase...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}\n")
    
    connect_supabase()

