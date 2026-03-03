import psycopg2
import requests
import numpy as np
import json
import time
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("embedding_updates.log"),
        logging.StreamHandler()
    ]
)

def get_embedding(text, model="bge-m3:latest"):
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
            logging.error(f"Error getting embedding: {response.status_code}")
            logging.error(response.text)
            return None
    except Exception as e:
        logging.error(f"Exception during embedding request: {e}")
        return None

def setup_database():
    """Set up the database with pgvector extension and required tables"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if pgvector extension exists, if not create it
        cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        if not cur.fetchone():
            logging.info("Creating pgvector extension...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Check if VectorNews table exists, if not create it
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA' 
            AND table_name = 'VectorNews'
        """)
        
        if not cur.fetchone():
            logging.info("Creating VectorNews table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS "NBA"."VectorNews"
                (
                    "NewsID" integer NOT NULL,
                    "NewsVector" vector(1024) NOT NULL,
                    CONSTRAINT "VectorNews_pkey" PRIMARY KEY ("NewsID")
                )
            """)
        
        # Create an index for faster similarity searches if it doesn't exist
        try:
            cur.execute("""
                SELECT 1 FROM pg_indexes 
                WHERE schemaname = 'NBA' 
                AND tablename = 'VectorNews' 
                AND indexname = 'vectornews_hnsw_idx'
            """)
            
            if not cur.fetchone():
                logging.info("Creating HNSW index for faster similarity searches...")
                try:
                    cur.execute("""
                        CREATE INDEX vectornews_hnsw_idx
                        ON "NBA"."VectorNews" 
                        USING hnsw ("NewsVector" vector_cosine_ops)
                        WITH (m = 16, ef_construction = 64)
                    """)
                    logging.info("HNSW index created successfully.")
                except Exception as e:
                    logging.warning(f"Could not create HNSW index: {e}")
                    logging.info("Trying IVF index instead...")
                    try:
                        cur.execute("""
                            CREATE INDEX vectornews_ivf_idx
                            ON "NBA"."VectorNews" 
                            USING ivfflat ("NewsVector" vector_cosine_ops)
                            WITH (lists = 100)
                        """)
                        logging.info("IVF index created successfully.")
                    except Exception as e:
                        logging.warning(f"Could not create IVF index: {e}")
                        logging.info("Continuing without index. Searches will be slower.")
        except Exception as e:
            logging.warning(f"Error checking for existing index: {e}")
        
        cur.close()
        conn.close()
        logging.info("Database setup complete")
        return True
    except Exception as e:
        logging.error(f"Error setting up database: {e}")
        return False

def fetch_news_without_embeddings(limit=100):
    """Fetch news articles that don't have embeddings yet"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Get news that don't have entries in the VectorNews table
        cur.execute("""
            SELECT n."NewsID", n."Title", n."Content"
            FROM "NBA"."News" n
            LEFT JOIN "NBA"."VectorNews" v ON n."NewsID" = v."NewsID"
            WHERE v."NewsID" IS NULL
            LIMIT %s
        """, (limit,))
        
        news = cur.fetchall()
        cur.close()
        conn.close()
        
        return news
    except Exception as e:
        logging.error(f"Error fetching news without embeddings: {e}")
        return []

def update_news_with_embedding(news_id, embedding):
    """Update a news article with its embedding"""
    if not embedding:
        return False
        
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Insert or update the embedding in VectorNews table
        cur.execute("""
            INSERT INTO "NBA"."VectorNews" ("NewsID", "NewsVector")
            VALUES (%s, %s)
            ON CONFLICT ("NewsID") 
            DO UPDATE SET "NewsVector" = EXCLUDED."NewsVector"
        """, (news_id, embedding))
        
        success = True
    except Exception as e:
        logging.error(f"Error updating news {news_id} with embedding: {e}")
        conn.rollback()
        success = False
    finally:
        cur.close()
        conn.close()
    
    return success

def process_news_embeddings(batch_size=10, max_retries=3):
    """Process news articles and generate embeddings in batches with retry logic"""
    # First make sure Ollama is running and the model is available
    try:
        response = requests.get("http://localhost:11434/api/tags")
        models = [model["name"] for model in response.json()["models"]]
        if "bge-m3:latest" not in models:
            logging.error("bge-m3:latest model not found in Ollama. Please run 'ollama pull bge-m3' first.")
            return
    except Exception as e:
        logging.error(f"Error connecting to Ollama: {e}")
        logging.error("Make sure Ollama is running on localhost:11434")
        return
    
    news_items = fetch_news_without_embeddings()
    logging.info(f"Found {len(news_items)} news articles without embeddings")
    
    if not news_items:
        logging.info("No news articles to process.")
        return
    
    # Process in batches
    total = len(news_items)
    successful = 0
    failed = 0
    
    for i in range(0, total, batch_size):
        batch = news_items[i:i+batch_size]
        logging.info(f"Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size} ({i}/{total})")
        
        for news_id, title, content in batch:
            # Combine title and content for better context
            full_text = f"{title}\n\n{content}"
            
            # Try with retries
            for attempt in range(max_retries):
                embedding = get_embedding(full_text)
                if embedding:
                    success = update_news_with_embedding(news_id, embedding)
                    if success:
                        logging.info(f"Updated news ID {news_id} with embedding")
                        successful += 1
                        break
                    else:
                        logging.warning(f"Failed to update news ID {news_id}, attempt {attempt+1}/{max_retries}")
                else:
                    logging.warning(f"Failed to get embedding for news ID {news_id}, attempt {attempt+1}/{max_retries}")
                
                if attempt < max_retries - 1:
                    # Wait before retry with exponential backoff
                    wait_time = 0.5 * (2 ** attempt)
                    logging.info(f"Waiting {wait_time:.1f} seconds before retry...")
                    time.sleep(wait_time)
            else:
                # This executes if the for loop completes without a break (all retries failed)
                logging.error(f"Failed to process news ID {news_id} after {max_retries} attempts")
                failed += 1
            
            # Sleep briefly to avoid overwhelming Ollama
            time.sleep(0.5)
    
    logging.info(f"Embedding process complete. Successful: {successful}, Failed: {failed}")

def search_similar_news(query_text, top_k=5, similarity_threshold=0.7):
    """Search for news similar to the query text using cosine similarity"""
    # Get embedding for the query
    query_embedding = get_embedding(query_text)
    if not query_embedding:
        logging.error("Failed to get embedding for search query")
        return []
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Set ef_search parameter for HNSW index (if using HNSW)
        try:
            cur.execute("SET hnsw.ef_search = 100")
        except:
            pass  # Ignore if not supported
        
        # Format the embedding as a PostgreSQL vector string
        vector_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        # Calculate cosine similarity and return top_k results
        cur.execute("""
            SELECT n."NewsID", n."Title", n."Date", n."Source", n."Author", 
                   1 - (v."NewsVector" <=> %s::vector) as similarity
            FROM "NBA"."News" n
            JOIN "NBA"."VectorNews" v ON n."NewsID" = v."NewsID"
            WHERE 1 - (v."NewsVector" <=> %s::vector) > %s
            ORDER BY v."NewsVector" <=> %s::vector
            LIMIT %s
        """, (vector_str, vector_str, similarity_threshold, vector_str, top_k))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return results
    except Exception as e:
        logging.error(f"Error searching similar news: {e}")
        return []

if __name__ == "__main__":
    # Pull the model if not already downloaded
    logging.info("Checking if bge-m3:latest model is available...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        models = [model["name"] for model in response.json()["models"]]
        if "bge-m3:latest" not in models:
            logging.info("Pulling bge-m3 model (this may take a while)...")
            os.system("ollama pull bge-m3")
        else:
            logging.info("bge-m3:latest model is already available")
    except Exception as e:
        logging.error(f"Error checking Ollama models: {e}")
        logging.error("Please make sure Ollama is running and pull the model manually with 'ollama pull bge-m3'")
    
    # Setup database with pgvector
    if setup_database():
        # Process news embeddings
        logging.info("Processing news embeddings...")
        process_news_embeddings()
        
        # Example of searching similar news
        # Uncomment to test
        # query = "NBA playoffs"
        # results = search_similar_news(query)
        # logging.info(f"Top results for '{query}':")
        # for result in results:
        #     logging.info(f"ID: {result[0]}, Title: {result[1]}, Similarity: {result[5]:.4f}")
    else:
        logging.error("Database setup failed. Please check the logs for details.") 