import psycopg2
import requests
import numpy as np
import json
import time
import psycopg2.extras

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

def setup_database():
    """Set up the database with pgvector extension and required columns"""
    conn = psycopg2.connect(
        host='localhost',
        dbname='James',
        user='postgres',
        password='jcjc1749'
    )
    cur = conn.cursor()
    
    # Check if pgvector extension exists, if not create it
    cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
    if not cur.fetchone():
        print("Creating pgvector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
    
    # Check if embedding column exists, if not create it
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'NBA' 
        AND table_name = 'News' 
        AND column_name = 'Embedding'
    """)
    
    if not cur.fetchone():
        print("Adding Embedding column to News table")
        cur.execute("""
            ALTER TABLE "NBA"."News"
            ADD COLUMN "Embedding" vector(1024)
        """)
        conn.commit()
    
    cur.close()
    conn.close()
    print("Database setup complete")

def fetch_news_without_embeddings():
    """Fetch news articles that don't have embeddings yet"""
    conn = psycopg2.connect(
        host='localhost',
        dbname='James',
        user='postgres',
        password='jcjc1749'
    )
    cur = conn.cursor()
    
    # Get news without embeddings
    cur.execute("""
        SELECT "NewsID", "Title", "Content"
        FROM "NBA"."News"
        WHERE "Embedding" IS NULL
    """)
    
    news = cur.fetchall()
    cur.close()
    conn.close()
    
    return news

def update_news_with_embedding(news_id, embedding):
    """Update a news article with its embedding"""
    if not embedding:
        return False
        
    conn = psycopg2.connect(
        host='localhost',
        dbname='James',
        user='postgres',
        password='jcjc1749'
    )
    cur = conn.cursor()
    
    try:
        # Convert embedding to PostgreSQL vector format
        embedding_array = np.array(embedding)
        
        # Register the vector type with psycopg2
        psycopg2.extras.register_vector()
        
        cur.execute("""
            UPDATE "NBA"."News"
            SET "Embedding" = %s
            WHERE "NewsID" = %s
        """, (embedding_array, news_id))
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error updating news {news_id} with embedding: {e}")
        conn.rollback()
        success = False
    
    cur.close()
    conn.close()
    return success

# Main execution
if __name__ == "__main__":
    # Setup database
    print("Setting up database...")
    setup_database()
    
    # Fetch news without embeddings
    news = fetch_news_without_embeddings()
    print(f"Found {len(news)} news articles without embeddings")
    
    # Process a sample article if available
    if news:
        # Get the first news article
        news_id, title, content = news[0]
        print(f"Sample news ID: {news_id}")
        print(f"Title: {title}")
        
        # Generate embedding
        print("Generating embedding...")
        sample_text = f"{title}\n\n{content}"
        embedding = get_embedding(sample_text)
        
        if embedding:
            print(f"Sample embedding length: {len(embedding)}")
            print(f"Sample embedding format: {type(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
            print(f"Value range: {min(embedding)} to {max(embedding)}")
            
            # Update the news with embedding
            print("Updating database...")
            success = update_news_with_embedding(news_id, embedding)
            print(f"Updated database: {success}")
        else:
            print("Failed to generate embedding. Make sure Ollama is running with bge-m3 model.")
    else:
        print("No news articles without embeddings found.") 