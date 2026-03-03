from db_config import get_connection, DB_SCHEMA
import psycopg2

def migrate():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Add ImageStatus column if it doesn't exist
        cur.execute(f"ALTER TABLE \"{DB_SCHEMA}\".\"News\" ADD COLUMN IF NOT EXISTS \"ImageStatus\" TEXT DEFAULT 'pending';")
        
        # Add ImagePrompt column if it doesn't exist
        cur.execute(f"ALTER TABLE \"{DB_SCHEMA}\".\"News\" ADD COLUMN IF NOT EXISTS \"ImagePrompt\" TEXT;")
        
        # Update existing news without images to 'pending'
        cur.execute(f"UPDATE \"{DB_SCHEMA}\".\"News\" SET \"ImageStatus\" = 'pending' WHERE \"ImageURL\" IS NULL;")
        
        # Update existing news with images to 'completed'
        cur.execute(f"UPDATE \"{DB_SCHEMA}\".\"News\" SET \"ImageStatus\" = 'completed' WHERE \"ImageURL\" IS NOT NULL;")
        
        conn.commit()
        print("Migration successful: Added ImageStatus and ImagePrompt columns to News table.")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
