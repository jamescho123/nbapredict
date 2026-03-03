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
        logging.FileHandler("player_embedding.log"),
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
        
        # Check if VectorPlayers table exists, if not create it
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA' 
            AND table_name = 'VectorPlayers'
        """)
        
        if not cur.fetchone():
            logging.info("Creating VectorPlayers table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS "NBA"."VectorPlayers"
                (
                    "PlayerID" integer NOT NULL,
                    "PlayerVector" vector(1024) NOT NULL,
                    CONSTRAINT "VectorPlayers_pkey" PRIMARY KEY ("PlayerID")
                )
            """)
        
        # Create an index for faster similarity searches if it doesn't exist
        try:
            cur.execute("""
                SELECT 1 FROM pg_indexes 
                WHERE schemaname = 'NBA' 
                AND tablename = 'VectorPlayers' 
                AND indexname = 'vectorplayers_hnsw_idx'
            """)
            
            if not cur.fetchone():
                logging.info("Creating HNSW index for faster similarity searches...")
                try:
                    cur.execute("""
                        CREATE INDEX vectorplayers_hnsw_idx
                        ON "NBA"."VectorPlayers" 
                        USING hnsw ("PlayerVector" vector_cosine_ops)
                        WITH (m = 16, ef_construction = 64)
                    """)
                    logging.info("HNSW index created successfully.")
                except Exception as e:
                    logging.warning(f"Could not create HNSW index: {e}")
                    logging.info("Trying IVF index instead...")
                    try:
                        cur.execute("""
                            CREATE INDEX vectorplayers_ivf_idx
                            ON "NBA"."VectorPlayers" 
                            USING ivfflat ("PlayerVector" vector_cosine_ops)
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

def fetch_players_without_embeddings(limit=100):
    """Fetch players that don't have embeddings yet"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Get players that don't have entries in the VectorPlayers table
        cur.execute("""
            SELECT p."PlayerID", p."PlayerName", p."Position", p."Height", p."Weight", 
                   p."Colleges", p."Country", p."Number"
            FROM "NBA"."Players" p
            LEFT JOIN "NBA"."VectorPlayers" v ON p."PlayerID" = v."PlayerID"
            WHERE v."PlayerID" IS NULL
            LIMIT %s
        """, (limit,))
        
        players = cur.fetchall()
        cur.close()
        conn.close()
        
        return players
    except Exception as e:
        logging.error(f"Error fetching players without embeddings: {e}")
        return []

def update_player_with_embedding(player_id, embedding):
    """Update a player with its embedding"""
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
        
        # Insert or update the embedding in VectorPlayers table
        cur.execute("""
            INSERT INTO "NBA"."VectorPlayers" ("PlayerID", "PlayerVector")
            VALUES (%s, %s)
            ON CONFLICT ("PlayerID") 
            DO UPDATE SET "PlayerVector" = EXCLUDED."PlayerVector"
        """, (player_id, embedding))
        
        success = True
    except Exception as e:
        logging.error(f"Error updating player {player_id} with embedding: {e}")
        conn.rollback()
        success = False
    finally:
        cur.close()
        conn.close()
    
    return success

def embed_all_players(batch_size=20, sleep_between_batches=5):
    """Process all players without embeddings in batches"""
    logging.info("Starting player embedding process")
    
    # Setup database first
    if not setup_database():
        logging.error("Database setup failed. Aborting.")
        return
    
    total_processed = 0
    total_successful = 0
    total_failed = 0
    
    while True:
        # Fetch a batch of players without embeddings
        player_batch = fetch_players_without_embeddings(batch_size)
        
        if not player_batch:
            logging.info("No more players to process. Done!")
            break
        
        batch_count = len(player_batch)
        logging.info(f"Processing batch of {batch_count} players")
        
        successful = 0
        failed = 0
        
        # Process each player in the batch
        for player in player_batch:
            try:
                player_id = player[0]
                player_name = player[1]
                position = player[2]
                height = player[3]
                weight = player[4]
                colleges = player[5]
                country = player[6]
                number = player[7]
                
                # Create a text representation of player stats
                player_text = f"Player: {player_name}\n"
                player_text += f"Position: {position}\n" if position else ""
                player_text += f"Height: {height} inches\n" if height else ""
                player_text += f"Weight: {weight} lbs\n" if weight else ""
                player_text += f"College: {colleges}\n" if colleges else ""
                player_text += f"Country: {country}\n" if country else ""
                player_text += f"Number: {number}\n" if number else ""
                
                # Get embedding
                logging.info(f"Getting embedding for player ID {player_id}: {player_name}")
                embedding = get_embedding(player_text)
                
                if embedding:
                    # Update player with embedding
                    if update_player_with_embedding(player_id, embedding):
                        logging.info(f"Successfully embedded player ID {player_id}")
                        successful += 1
                    else:
                        logging.error(f"Failed to update player ID {player_id} with embedding")
                        failed += 1
                else:
                    logging.error(f"Failed to get embedding for player ID {player_id}")
                    failed += 1
                
                # Brief pause to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                logging.error(f"Error processing player ID {player_id}: {e}")
                failed += 1
        
        # Update totals
        total_processed += batch_count
        total_successful += successful
        total_failed += failed
        
        logging.info(f"Batch complete. Successful: {successful}, Failed: {failed}")
        logging.info(f"Total progress: Processed {total_processed}, Successful: {total_successful}, Failed: {total_failed}")
        
        # Sleep between batches to give the system a break
        if sleep_between_batches > 0:
            logging.info(f"Sleeping for {sleep_between_batches} seconds before next batch...")
            time.sleep(sleep_between_batches)
    
    logging.info(f"Player embedding process complete!")
    logging.info(f"Total players processed: {total_processed}")
    logging.info(f"Total successful: {total_successful}")
    logging.info(f"Total failed: {total_failed}")

def search_similar_players(query_text, top_k=5, similarity_threshold=0.7):
    """Search for players similar to the query text using cosine similarity"""
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
            SELECT p."PlayerID", p."PlayerName", p."Position", p."Height", p."Weight",
                   1 - (v."PlayerVector" <=> %s::vector) as similarity
            FROM "NBA"."Players" p
            JOIN "NBA"."VectorPlayers" v ON p."PlayerID" = v."PlayerID"
            WHERE 1 - (v."PlayerVector" <=> %s::vector) > %s
            ORDER BY v."PlayerVector" <=> %s::vector
            LIMIT %s
        """, (vector_str, vector_str, similarity_threshold, vector_str, top_k))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return results
    except Exception as e:
        logging.error(f"Error searching similar players: {e}")
        return []

if __name__ == "__main__":
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            logging.error("Ollama server is not running. Please start it first.")
            raise NotImplementedError("Ollama server is not running")
    except Exception as e:
        logging.error(f"Error connecting to Ollama: {e}")
        logging.error("Make sure Ollama is running on localhost:11434")
        raise NotImplementedError("Ollama server is not running")
    
    # Start embedding process
    embed_all_players()