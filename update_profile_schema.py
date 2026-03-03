import psycopg2
from db_config import DB_CONFIG

def migrate_user_preferences():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Check if columns exist, if not add them
        columns_to_add = [
            ('FavoriteTeams', 'TEXT[]'), # Changed to array for multiple teams
            ('Age', 'INTEGER'),
            ('Country', 'TEXT'),
            ('State', 'TEXT'),
            ('City', 'TEXT'),
            ('Gender', 'TEXT')
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cur.execute(f'''
                    ALTER TABLE "NBA"."UserPreferences" 
                    ADD COLUMN "{col_name}" {col_type};
                ''')
                print(f"Added column {col_name}")
            except psycopg2.errors.DuplicateColumn:
                print(f"Column {col_name} already exists")
                conn.rollback()
                continue
            conn.commit()
            
        # Also migrate existing 'FavoriteTeam' (singular) to 'FavoriteTeams' (array) if needed
        # For now, we'll keep both or switch logic in python
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate_user_preferences()
