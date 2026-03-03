import psycopg2
import numpy as np

def fetch_news_sample():
    """Fetch a sample news article from the database"""
    conn = psycopg2.connect(
        host='localhost',
        dbname='James',
        user='postgres',
        password='jcjc1749'
    )
    cur = conn.cursor()
    
    # Get a sample news article
    cur.execute("""
        SELECT "NewsID", "Title", "Content"
        FROM "NBA"."News"
        LIMIT 1
    """)
    
    news = cur.fetchone()
    cur.close()
    conn.close()
    
    return news

# Main execution
if __name__ == "__main__":
    # Fetch a sample news article
    news = fetch_news_sample()
    
    if news:
        # Get the news article details
        news_id, title, content = news
        print(f"Sample news ID: {news_id}")
        print(f"Title: {title}")
        
        # Create a mock embedding (1024-dimensional vector with random values)
        print("\nGenerating mock embedding (since Ollama is not available)...")
        mock_embedding = np.random.uniform(-1, 1, 1024).tolist()
        
        print("\nEMBEDDING FORMAT:")
        print(f"Type: {type(mock_embedding)}")
        print(f"Length: {len(mock_embedding)}")
        print(f"First 5 values: {mock_embedding[:5]}")
        print(f"Last 5 values: {mock_embedding[-5:]}")
        print(f"Value range: {min(mock_embedding)} to {max(mock_embedding)}")
        
        # Show numpy array format (which would be used for database storage)
        embedding_array = np.array(mock_embedding)
        print("\nNUMPY ARRAY FORMAT (for database storage):")
        print(f"Type: {type(embedding_array)}")
        print(f"Shape: {embedding_array.shape}")
        print(f"Data type: {embedding_array.dtype}")
        
        # Show a sample of how it would be stored in the database
        print("\nSAMPLE DATABASE REPRESENTATION:")
        print("The vector would be stored as a 1024-dimensional vector in PostgreSQL with pgvector")
        print("Example SQL: UPDATE \"NBA\".\"News\" SET \"Embedding\" = [1024 dimensional vector] WHERE \"NewsID\" = 123")
        
        print("\nTO IMPLEMENT EMBEDDINGS IN YOUR DATABASE:")
        print("1. Install pgvector extension on your PostgreSQL server")
        print("   - Run: CREATE EXTENSION vector; (as superuser)")
        print("2. Alter your table to add the embedding column:")
        print("   - ALTER TABLE \"NBA\".\"News\" ADD COLUMN \"Embedding\" vector(1024);")
        print("3. Start Ollama service and pull the bge-m3 model")
        print("4. Run the news_embedding.py script to process your news articles")
    else:
        print("No news articles found in the database.") 