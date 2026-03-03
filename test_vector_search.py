import psycopg2
import requests
import json

def get_embedding(text, model="bge-m3:latest"):
    """Get embeddings from Ollama API using the specified model"""
    url = "http://localhost:11434/api/embeddings"
    
    payload = {
        "model": model,
        "prompt": text
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        print(f"Error getting embedding: {response.status_code}")
        print(response.text)
        return None

def test_vector_search():
    """Test vector search functionality directly"""
    print("===== Testing Vector Search =====")
    
    # Sample query
    query = "Lakers Deandre Ayton"
    print(f"\nQuery: {query}")
    
    # Get embedding for the query
    print("\nGetting embedding for query...")
    query_embedding = get_embedding(query)
    
    if not query_embedding:
        print("Failed to get embedding for query.")
        return
    
    print(f"Got embedding with {len(query_embedding)} dimensions")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # First, check if we have any vectors in the database
        cur.execute('SELECT COUNT(*) FROM "NBA"."VectorNews"')
        count = cur.fetchone()[0]
        print(f"\nNumber of vectors in database: {count}")
        
        if count == 0:
            print("No vectors in database. Cannot perform search.")
            return
        
        # Try a simple vector search
        print("\nPerforming vector search...")
        
        # Format the embedding as a PostgreSQL vector string
        vector_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        # Try direct SQL approach
        cur.execute("""
            SELECT v."NewsID", n."Title", 
                   1 - (v."NewsVector" <=> %s::vector) as similarity
            FROM "NBA"."VectorNews" v
            JOIN "NBA"."News" n ON v."NewsID" = n."NewsID"
            ORDER BY v."NewsVector" <=> %s::vector
            LIMIT 5
        """, (vector_str, vector_str))
        
        results = cur.fetchall()
        
        if results:
            print(f"\nFound {len(results)} similar articles:")
            for i, (news_id, title, similarity) in enumerate(results):
                print(f"  {i+1}. {title} (similarity: {similarity:.4f})")
                
                # Fetch the content
                cur.execute("""
                    SELECT "Content" FROM "NBA"."News" WHERE "NewsID" = %s
                """, (news_id,))
                content = cur.fetchone()[0]
                print(f"     First 100 chars: {content[:100]}...")
        else:
            print("No results found.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error during vector search: {e}")

if __name__ == "__main__":
    test_vector_search() 