import psycopg2

def check_database_status():
    """Check the status of the database tables and embeddings"""
    print("===== Database Status Check =====")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Check if pgvector extension is installed
        cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
        vector_ext = cur.fetchone()
        if vector_ext:
            print(f"pgvector extension: Installed (version {vector_ext[1]})")
        else:
            print("pgvector extension: NOT installed")
        
        # Check News table
        cur.execute("SELECT COUNT(*) FROM \"NBA\".\"News\"")
        news_count = cur.fetchone()[0]
        print(f"News articles: {news_count}")
        
        # Check VectorNews table
        try:
            cur.execute("SELECT COUNT(*) FROM \"NBA\".\"VectorNews\"")
            vector_count = cur.fetchone()[0]
            print(f"Articles with embeddings: {vector_count}")
            
            if news_count > 0:
                percentage = (vector_count / news_count) * 100
                print(f"Embedding coverage: {percentage:.1f}%")
        except Exception as e:
            print(f"Error checking VectorNews table: {e}")
        
        # Check for indexes
        cur.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE schemaname = 'NBA' AND tablename = 'VectorNews'
        """)
        indexes = cur.fetchall()
        
        if indexes:
            print("\nVector indexes:")
            for idx_name, idx_def in indexes:
                print(f"  - {idx_name}: {idx_def}")
        else:
            print("\nNo vector indexes found.")
        
        # Sample a few news articles
        print("\nSample news articles:")
        cur.execute("""
            SELECT n."NewsID", n."Title", n."Date" 
            FROM "NBA"."News" n 
            ORDER BY n."NewsID" 
            LIMIT 5
        """)
        for row in cur.fetchall():
            print(f"  ID: {row[0]}, Title: {row[1]}, Date: {row[2]}")
        
        # Sample vector news entries
        print("\nSample vector entries:")
        try:
            cur.execute("""
                SELECT v."NewsID", n."Title", 
                       substring(v."NewsVector"::text, 1, 50) as vector_sample
                FROM "NBA"."VectorNews" v
                JOIN "NBA"."News" n ON v."NewsID" = n."NewsID"
                LIMIT 3
            """)
            for row in cur.fetchall():
                print(f"  ID: {row[0]}, Title: {row[1]}")
                print(f"  Vector sample: {row[2]}...")
        except Exception as e:
            print(f"Error sampling vector entries: {e}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_database_status() 