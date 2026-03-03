import psycopg2

def check_postgres():
    """Check PostgreSQL connection and version"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Get PostgreSQL version
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"Connected to PostgreSQL: {version}")
        
        # Get PostgreSQL data directory
        cur.execute("SHOW data_directory")
        data_dir = cur.fetchone()[0]
        print(f"PostgreSQL data directory: {data_dir}")
        
        # Get extension directory
        cur.execute("SHOW extension_destdir")
        ext_dir = cur.fetchone()
        if ext_dir and ext_dir[0]:
            print(f"Extension directory: {ext_dir[0]}")
        else:
            print("Extension directory not explicitly set (using default)")
        
        # Check for pgvector in available extensions
        cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
        pgvector_info = cur.fetchone()
        if pgvector_info:
            print(f"pgvector is available: {pgvector_info}")
        else:
            print("pgvector extension is NOT available in pg_available_extensions")
        
        # Check for installed extensions
        cur.execute("SELECT name, default_version, installed_version FROM pg_available_extensions WHERE installed_version IS NOT NULL")
        installed_extensions = cur.fetchall()
        print("\nInstalled extensions:")
        for ext in installed_extensions:
            print(f"- {ext[0]} (version {ext[2]})")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")

if __name__ == "__main__":
    check_postgres() 