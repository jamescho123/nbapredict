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
        logging.FileHandler("team_embedding.log"),
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
        
        # Check if VectorTeams table exists, if not create it
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA' 
            AND table_name = 'VectorTeams'
        """)
        
        if not cur.fetchone():
            logging.info("Creating VectorTeams table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS "NBA"."VectorTeams"
                (
                    "TeamID" integer NOT NULL,
                    "TeamVector" vector(1024) NOT NULL,
                    CONSTRAINT "VectorTeams_pkey" PRIMARY KEY ("TeamID")
                )
            """)
        
        # Create an index for faster similarity searches if it doesn't exist
        try:
            cur.execute("""
                SELECT 1 FROM pg_indexes 
                WHERE schemaname = 'NBA' 
                AND tablename = 'VectorTeams' 
                AND indexname = 'vectorteams_hnsw_idx'
            """)
            
            if not cur.fetchone():
                logging.info("Creating HNSW index for faster similarity searches...")
                try:
                    cur.execute("""
                        CREATE INDEX vectorteams_hnsw_idx
                        ON "NBA"."VectorTeams" 
                        USING hnsw ("TeamVector" vector_cosine_ops)
                        WITH (m = 16, ef_construction = 64)
                    """)
                    logging.info("HNSW index created successfully.")
                except Exception as e:
                    logging.warning(f"Could not create HNSW index: {e}")
                    logging.info("Trying IVF index instead...")
                    try:
                        cur.execute("""
                            CREATE INDEX vectorteams_ivf_idx
                            ON "NBA"."VectorTeams" 
                            USING ivfflat ("TeamVector" vector_cosine_ops)
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

def fetch_teams_without_embeddings(limit=100):
    """Fetch teams that don't have embeddings yet"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Get teams that don't have entries in the VectorTeams table
        cur.execute("""
            SELECT t."TeamID", t."TeamName", t."Conference", t."Division", 
                   t."WinPercentage", t."Playoffs", t."ConferenceChampion", t."Championship"
            FROM "NBA"."Teams" t
            LEFT JOIN "NBA"."VectorTeams" v ON t."TeamID" = v."TeamID"
            WHERE v."TeamID" IS NULL
            LIMIT %s
        """, (limit,))
        
        teams = cur.fetchall()
        cur.close()
        conn.close()
        
        return teams
    except Exception as e:
        logging.error(f"Error fetching teams without embeddings: {e}")
        return []

def update_team_with_embedding(team_id, embedding):
    """Update a team with its embedding"""
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
        
        # Insert or update the embedding in VectorTeams table
        cur.execute("""
            INSERT INTO "NBA"."VectorTeams" ("TeamID", "TeamVector")
            VALUES (%s, %s)
            ON CONFLICT ("TeamID") 
            DO UPDATE SET "TeamVector" = EXCLUDED."TeamVector"
        """, (team_id, embedding))
        
        success = True
    except Exception as e:
        logging.error(f"Error updating team {team_id} with embedding: {e}")
        conn.rollback()
        success = False
    finally:
        cur.close()
        conn.close()
    
    return success

def embed_all_teams(batch_size=20, sleep_between_batches=5):
    """Process all teams without embeddings in batches"""
    logging.info("Starting team embedding process")
    
    # Setup database first
    if not setup_database():
        logging.error("Database setup failed. Aborting.")
        return
    
    total_processed = 0
    total_successful = 0
    total_failed = 0
    
    while True:
        # Fetch a batch of teams without embeddings
        team_batch = fetch_teams_without_embeddings(batch_size)
        
        if not team_batch:
            logging.info("No more teams to process. Done!")
            break
        
        batch_count = len(team_batch)
        logging.info(f"Processing batch of {batch_count} teams")
        
        successful = 0
        failed = 0
        
        # Process each team in the batch
        for team in team_batch:
            try:
                team_id = team[0]
                team_name = team[1]
                conference = team[2]
                division = team[3]
                win_percentage = team[4]
                playoffs = team[5]
                conf_champion = team[6]
                championship = team[7]
                
                # Create a text representation of team stats
                team_text = f"Team: {team_name}\n"
                team_text += f"Conference: {conference}\n" if conference else ""
                team_text += f"Division: {division}\n" if division else ""
                team_text += f"Win Percentage: {win_percentage}\n" if win_percentage else ""
                team_text += f"Playoff Appearances: {playoffs}\n" if playoffs else ""
                team_text += f"Conference Championships: {conf_champion}\n" if conf_champion else ""
                team_text += f"NBA Championships: {championship}\n" if championship else ""
                
                # Get embedding
                logging.info(f"Getting embedding for team ID {team_id}: {team_name}")
                embedding = get_embedding(team_text)
                
                if embedding:
                    # Update team with embedding
                    if update_team_with_embedding(team_id, embedding):
                        logging.info(f"Successfully embedded team ID {team_id}")
                        successful += 1
                    else:
                        logging.error(f"Failed to update team ID {team_id} with embedding")
                        failed += 1
                else:
                    logging.error(f"Failed to get embedding for team ID {team_id}")
                    failed += 1
                
                # Brief pause to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                logging.error(f"Error processing team ID {team_id}: {e}")
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
    
    logging.info(f"Team embedding process complete!")
    logging.info(f"Total teams processed: {total_processed}")
    logging.info(f"Total successful: {total_successful}")
    logging.info(f"Total failed: {total_failed}")

def search_similar_teams(query_text, top_k=5, similarity_threshold=0.7):
    """Search for teams similar to the query text using cosine similarity"""
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
            SELECT t."TeamID", t."TeamName", t."Conference", t."Division", t."WinPercentage",
                   1 - (v."TeamVector" <=> %s::vector) as similarity
            FROM "NBA"."Teams" t
            JOIN "NBA"."VectorTeams" v ON t."TeamID" = v."TeamID"
            WHERE 1 - (v."TeamVector" <=> %s::vector) > %s
            ORDER BY v."TeamVector" <=> %s::vector
            LIMIT %s
        """, (vector_str, vector_str, similarity_threshold, vector_str, top_k))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return results
    except Exception as e:
        logging.error(f"Error searching similar teams: {e}")
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
    embed_all_teams()