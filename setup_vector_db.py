import psycopg2
import os

def setup_vector_database():
    """Set up a vector database following the programmer.ie approach"""
    
    # Database connection parameters
    conn_params = {
        'host': 'localhost',
        'dbname': 'James',
        'user': 'postgres',
        'password': 'jcjc1749'
    }
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if vector extension is available
        cur.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
        if not cur.fetchone():
            print("Error: vector extension is not available in PostgreSQL.")
            print("Please install pgvector extension first using install_pgvector.py")
            return False
        
        # Create vector extension if not already created
        print("Creating vector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Check if News table exists in NBA schema
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema = 'NBA' AND table_name = 'News'")
        if not cur.fetchone():
            print("Error: NBA.News table does not exist.")
            return False
        
        # Add embedding column to News table if not exists
        print("Adding embedding column to News table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'NBA' 
            AND table_name = 'News' 
            AND column_name = 'Embedding'
        """)
        
        if not cur.fetchone():
            cur.execute("""
                ALTER TABLE "NBA"."News"
                ADD COLUMN "Embedding" vector(1024)
            """)
            print("Embedding column added successfully.")
        else:
            print("Embedding column already exists.")
        
        # Create an index for faster similarity searches
        print("Creating HNSW index for faster similarity searches...")
        try:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS news_embedding_hnsw_idx
                ON "NBA"."News" 
                USING hnsw ("Embedding" vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)
            print("HNSW index created successfully.")
        except Exception as e:
            print(f"Could not create HNSW index: {e}")
            print("Trying IVF index instead...")
            try:
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS news_embedding_ivf_idx
                    ON "NBA"."News" 
                    USING ivfflat ("Embedding" vector_cosine_ops)
                    WITH (lists = 100)
                """)
                print("IVF index created successfully.")
            except Exception as e:
                print(f"Could not create IVF index: {e}")
                print("Continuing without index. Searches will be slower.")
        
        print("\nVector database setup complete!")
        print("\nNext steps:")
        print("1. Run your news_embedding.py script to generate embeddings")
        print("2. Use the search_similar_news function to find similar articles")
        
        return True
        
    except Exception as e:
        print(f"Error setting up vector database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_vector_database() 