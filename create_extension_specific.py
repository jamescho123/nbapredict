import psycopg2

def create_vector_extension():
    """Create the vector extension in a specific PostgreSQL database"""
    
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
        
        # Check if the extension is already installed
        cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
        result = cur.fetchone()
        
        if result:
            print(f"Vector extension is already installed:")
            print(f"Name: {result[0]}")
            print(f"Version: {result[1]}")
            return True
        
        # Check if the extension is available
        cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
        available = cur.fetchone()
        
        if not available:
            print("Error: vector extension is not available in PostgreSQL.")
            print("Make sure the extension files are properly installed.")
            return False
        
        # Create the vector extension
        print("Creating vector extension...")
        try:
            cur.execute("CREATE EXTENSION vector")
            print("Extension creation command executed.")
            
            # Verify the extension was created
            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
            result = cur.fetchone()
            
            if result:
                print(f"Vector extension successfully installed!")
                print(f"Name: {result[0]}")
                print(f"Version: {result[1]}")
                return True
            else:
                print("Failed to install vector extension.")
                return False
        except Exception as e:
            print(f"Error during extension creation: {e}")
            return False
        
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    create_vector_extension() 