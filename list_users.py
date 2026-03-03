from db_config import get_connection, DB_SCHEMA

def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT "UserID", "Email", "Role" FROM "{DB_SCHEMA}"."Users"')
    for row in cursor.fetchall():
        print(row)
    conn.close()

if __name__ == "__main__":
    list_users()
