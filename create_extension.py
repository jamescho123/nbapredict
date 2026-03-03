import psycopg2
import sys

def test_connection():
    """Test connection to PostgreSQL and create pgvector extension"""
    print("===== PostgreSQL Connection Test and pgvector Setup =====")
    print()
    
    # Connection parameters
    params = {
        'host': 'localhost',
        'dbname': 'postgres',  # First try with default database
        'user': 'postgres',
        'password': 'jcjc1749'
    }
    
    try:
        print(f"Connecting to default database...")
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Test connection
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"Connected to PostgreSQL: {version[0]}")
        
        # Now try connecting to James database
        print("\nTrying to connect to 'James' database...")
        params['dbname'] = 'James'
        conn_james = psycopg2.connect(**params)
        conn_james.autocommit = True
        cur_james = conn_james.cursor()
        
        print("Connected to 'James' database successfully!")
        
        # Check if pgvector extension exists
        print("\nChecking if pgvector extension already exists...")
        cur_james.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        if cur_james.fetchone():
            print("pgvector extension is already installed!")
        else:
            print("pgvector extension is not installed. Attempting to create...")
            try:
                cur_james.execute("CREATE EXTENSION vector;")
                print("Successfully created pgvector extension!")
            except Exception as e:
                print(f"Error creating extension: {e}")
                print("\nThis could be because:")
                print("1. The pgvector files are not properly installed")
                print("2. You don't have sufficient privileges")
        
        # Verify installation
        print("\nVerifying pgvector installation...")
        cur_james.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
        result = cur_james.fetchone()
        if result:
            print(f"pgvector is installed: {result}")
            print("\nTrying a simple vector operation to confirm functionality...")
            try:
                cur_james.execute("SELECT '[1,2,3]'::vector")
                vector_result = cur_james.fetchone()
                print(f"Vector test result: {vector_result[0]}")
                print("\npgvector is fully functional!")
            except Exception as e:
                print(f"Error testing vector functionality: {e}")
        else:
            print("pgvector is NOT installed!")
        
        # Close connections
        cur.close()
        cur_james.close()
        conn.close()
        conn_james.close()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nThis could be because:")
        print("1. The password is incorrect")
        print("2. PostgreSQL service is not running")
        print("3. The database does not exist")
        return False
    
    return True

if __name__ == "__main__":
    success = test_connection()
    print("\nPress Enter to exit...", end="")
    input()
    sys.exit(0 if success else 1) 