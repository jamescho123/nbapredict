from db_config import get_connection, DB_SCHEMA
import psycopg2

def check_structure():
    conn = get_connection()
    cur = conn.cursor()
    
    print(f"Checking schema: {DB_SCHEMA}")
    
    # Check Users table
    try:
        cur.execute(f'SELECT * FROM "{DB_SCHEMA}"."Users" LIMIT 0')
        print("Users table columns:", [desc[0] for desc in cur.description])
    except Exception as e:
        print(f"Error checking Users table: {e}")
        conn.rollback()

    # Check for UserPreferences or similar for bans?
    # We might need to add a column.
    
    conn.close()

if __name__ == "__main__":
    check_structure()
