from db_config import get_connection, DB_SCHEMA
import psycopg2

def update_schema():
    conn = get_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    cursor = conn.cursor()
    
    try:
        print(f"Updating schema: {DB_SCHEMA}")
        
        # 1. Add Role column to Users if not exists
        print("Adding Role column...")
        cursor.execute(f'''
            ALTER TABLE "{DB_SCHEMA}"."Users" 
            ADD COLUMN IF NOT EXISTS "Role" VARCHAR(20) DEFAULT 'user';
        ''')
        
        # 2. Add IsBanned column to Users if not exists
        print("Adding IsBanned column...")
        cursor.execute(f'''
            ALTER TABLE "{DB_SCHEMA}"."Users" 
            ADD COLUMN IF NOT EXISTS "IsBanned" BOOLEAN DEFAULT FALSE;
        ''')
        
        # 3. Create PageVisibility table
        print("Creating PageVisibility table...")
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."PageVisibility" (
                "PageName" VARCHAR(50) PRIMARY KEY,
                "IsVisible" BOOLEAN DEFAULT TRUE,
                "MinRole" VARCHAR(20) DEFAULT 'user'
            );
        ''')
        
        # Insert default visibility settings
        default_pages = [
            ('Home', True, 'guest'),
            ('News', True, 'guest'),
            ('Ranking', True, 'guest'),
            ('Simple Predict', True, 'guest'),
            ('Hybrid Predict', True, 'user'),
            ('Check Stats', True, 'user'),

            ('Predict', True, 'user'),
            ('Entity Extraction', False, 'admin'),
            ('Profile', True, 'admin'),
            ('User_Management', True, 'admin'),
            ('Page_Management', True, 'admin')
        ]
        
        print("Inserting default page visibility settings...")
        for page, visible, role in default_pages:
            cursor.execute(f'''
                INSERT INTO "{DB_SCHEMA}"."PageVisibility" ("PageName", "IsVisible", "MinRole")
                VALUES (%s, %s, %s)
                ON CONFLICT ("PageName") DO NOTHING;
            ''', (page, visible, role))

        conn.commit()
        print("Schema update completed successfully!")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_schema()
