import psycopg2
import requests
import numpy as np
import json

def get_embedding(text, model="bge-m3"):
    """Get embeddings from Ollama API using the specified model"""
    url = "http://localhost:11434/api/embeddings"
    
    # Truncate text if too long (bge-m3 has context limits)
    if len(text) > 8192:
        text = text[:8192]
    
    payload = {
        "model": model,
        "prompt": text
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            print(f"Error getting embedding: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Exception during embedding request: {e}")
        return None

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
        
        # Generate embedding
        print("Generating embedding...")
        sample_text = f"{title}\n\n{content}"
        embedding = get_embedding(sample_text)
        
        if embedding:
            print("\nEMBEDDING FORMAT:")
            print(f"Type: {type(embedding)}")
            print(f"Length: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
            print(f"Last 5 values: {embedding[-5:]}")
            print(f"Value range: {min(embedding)} to {max(embedding)}")
            
            # Show numpy array format (which would be used for database storage)
            embedding_array = np.array(embedding)
            print("\nNUMPY ARRAY FORMAT (for database storage):")
            print(f"Type: {type(embedding_array)}")
            print(f"Shape: {embedding_array.shape}")
            print(f"Data type: {embedding_array.dtype}")
            
            # Show a sample of how it would be stored in the database
            print("\nSAMPLE DATABASE REPRESENTATION:")
            print("The vector would be stored as a 1024-dimensional vector in PostgreSQL")
            print("Example SQL: UPDATE \"NBA\".\"News\" SET \"Embedding\" = [1024 dimensional vector] WHERE \"NewsID\" = 123")
        else:
            print("Failed to generate embedding. Make sure Ollama is running with bge-m3 model.")
            print("You can start Ollama and pull the model with these commands:")
            print("1. Start Ollama service")
            print("2. Run: ollama pull bge-m3")
    else:
        print("No news articles found in the database.") 