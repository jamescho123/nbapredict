from db_config import get_connection, DB_SCHEMA

def check_user_status(email):
    conn = get_connection()
    if not conn:
        print("Database connection failed")
        return

    try:
        cursor = conn.cursor()
        print(f"Checking status for: {email}")
        
        cursor.execute(f'''
            SELECT "UserID", "Username", "Email", "Role" 
            FROM "{DB_SCHEMA}"."Users"
            WHERE "Email" = %s
        ''', (email,))
        
        user = cursor.fetchone()
        
        if user:
            print(f"User Found: ID={user[0]}")
            print(f"Username: {user[1]}")
            print(f"Email: {user[2]}")
            print(f"Role: {user[3]}")
        else:
            print("User not found in database.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_user_status("jamescho@jumbosoft.com")
