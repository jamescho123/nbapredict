from db_config import get_connection, DB_SCHEMA
import psycopg2

def check_users():
    conn = get_connection()
    if not conn:
        print("Failed to connect")
        return
        
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Users"')
        columns = [desc[0] for desc in cursor.description]
        print(f"Columns: {columns}")
        users = cursor.fetchall()
        print(f"Users found: {len(users)}")
        for user in users:
            print(user)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_users()
