
import psycopg2
from db_config import get_connection, DB_SCHEMA
import sys

def migrate():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check if URL column exists
        cur.execute(f"""
            SELECT count(*) 
            FROM information_schema.columns 
            WHERE table_schema = '{DB_SCHEMA}' 
            AND table_name = 'News' 
            AND column_name = 'URL';
        """)
        
        exists = cur.fetchone()[0] > 0
        
        if not exists:
            print(f"Adding URL column to {DB_SCHEMA}.News...")
            cur.execute(f'ALTER TABLE "{DB_SCHEMA}"."News" ADD COLUMN "URL" TEXT;')
            conn.commit()
            print("Successfully added URL column.")
        else:
            print("URL column already exists.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Migration error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
