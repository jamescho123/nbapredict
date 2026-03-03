from db_config import get_connection, DB_SCHEMA

def promote_to_admin(username_or_email):
    conn = get_connection()
    if not conn:
        print("Database connection failed")
        return

    try:
        cursor = conn.cursor()
        
        # Check if user exists
        print(f"Searching for user: {username_or_email}")
        cursor.execute(f'''
            SELECT "UserID", "Username", "Email", "Role" 
            FROM "{DB_SCHEMA}"."Users"
            WHERE "Username" = %s OR "Email" = %s
        ''', (username_or_email, username_or_email))
        
        user = cursor.fetchone()
        
        if not user:
            print(f"User '{username_or_email}' not found. Listing all users:")
            cursor.execute(f'SELECT "Username", "Email" FROM "{DB_SCHEMA}"."Users" LIMIT 50')
            for u in cursor.fetchall():
                print(f" - {u[0]} ({u[1]})")
            return

        print(f"Found user: ID={user[0]}, Username={user[1]}, Email={user[2]}, Current Role={user[3]}")
        
        # Update role
        cursor.execute(f'''
            UPDATE "{DB_SCHEMA}"."Users"
            SET "Role" = 'admin'
            WHERE "UserID" = %s
        ''', (user[0],))
        
        conn.commit()
        print(f"Successfully promoted '{user[1]}' to admin!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    promote_to_admin("jamescho@jumbosoft.com")
