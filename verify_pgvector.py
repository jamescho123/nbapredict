import psycopg2
import os

def verify_pgvector():
    """Verify if pgvector is available and installed"""
    
    # Database connection parameters
    dbname = input("Enter database name: ")
    user = input("Enter PostgreSQL username: ")
    password = input("Enter PostgreSQL password: ")
    host = input("Enter host (default: localhost): ") or "localhost"
    
    try:
        # Connect to PostgreSQL
        print(f"Connecting to PostgreSQL database '{dbname}' as user '{user}'...")
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check PostgreSQL version
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"Connected to PostgreSQL: {version}")
        
        # Check if pgvector is available
        cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
        available = cur.fetchone()
        
        if available:
            print("\npgvector is available:")
            print(f"Name: {available[0]}")
            print(f"Default version: {available[1]}")
            print(f"Installed version: {available[2] or 'Not installed'}")
            print(f"Comment: {available[3]}")
        else:
            print("\nError: pgvector extension is not available.")
            print("Make sure the extension files are properly installed.")
            return False
        
        # Check if pgvector is installed
        cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
        installed = cur.fetchone()
        
        if installed:
            print("\npgvector is installed:")
            print(f"Name: {installed[0]}")
            print(f"Version: {installed[1]}")
            print("\nSuccess! pgvector is properly installed and ready to use.")
        else:
            print("\npgvector is not installed in this database.")
            print("To install it, run: CREATE EXTENSION vector;")
        
        # Check for vector.dll in PostgreSQL lib directory
        pg_path = input("\nEnter your PostgreSQL installation path (e.g. C:\\Program Files\\PostgreSQL\\17): ")
        if pg_path and os.path.exists(pg_path):
            vector_dll = os.path.join(pg_path, "lib", "vector.dll")
            if os.path.exists(vector_dll):
                print(f"\nFound vector.dll at {vector_dll}")
                print(f"Size: {os.path.getsize(vector_dll)} bytes")
                print(f"Last modified: {os.path.getmtime(vector_dll)}")
            else:
                print(f"\nWarning: vector.dll not found at {vector_dll}")
                print("This could indicate an incomplete installation.")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    verify_pgvector() 