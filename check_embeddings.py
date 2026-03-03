#!/usr/bin/env python3
"""
Check and create vector embedding tables in PostgreSQL
"""

import psycopg2
import numpy as np

def check_database():
    """Check database structure and create embedding tables"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        print("🏀 NBA Database Vector Embedding Check")
        print("=" * 50)
        
        # Check existing tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA' 
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"📊 Available tables: {tables}")
        
        # Check for embedding tables
        embedding_tables = [t for t in tables if 'Embedding' in t]
        print(f"🧠 Embedding tables: {embedding_tables}")
        
        # Create embedding tables if they don't exist
        print("\n🔧 Creating embedding tables...")
        
        # Team embeddings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "NBA"."TeamEmbeddings" (
                "TeamID" INTEGER PRIMARY KEY,
                "Embedding" vector(1024),
                "Description" TEXT,
                "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ TeamEmbeddings table created/verified")
        
        # Player embeddings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "NBA"."PlayerEmbeddings" (
                "PlayerID" INTEGER PRIMARY KEY,
                "Embedding" vector(1024),
                "Description" TEXT,
                "TeamID" INTEGER,
                "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ PlayerEmbeddings table created/verified")
        
        # Match embeddings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "NBA"."MatchEmbeddings" (
                "GameID" INTEGER PRIMARY KEY,
                "Embedding" vector(1024),
                "Description" TEXT,
                "HomeTeam" VARCHAR(50),
                "AwayTeam" VARCHAR(50),
                "GameDate" DATE,
                "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ MatchEmbeddings table created/verified")
        
        # Check if vector extension is enabled
        try:
            cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
            if cur.fetchone():
                print("✅ Vector extension is enabled")
            else:
                print("⚠️ Vector extension not found. Trying to enable...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                print("✅ Vector extension enabled")
        except Exception as e:
            print(f"⚠️ Vector extension issue: {e}")
        
        # Check for existing data
        print("\n📊 Checking existing embedding data...")
        
        for table in ["TeamEmbeddings", "PlayerEmbeddings", "MatchEmbeddings"]:
            cur.execute(f'SELECT COUNT(*) FROM "NBA"."{table}";')
            count = cur.fetchone()[0]
            print(f"  {table}: {count} records")
        
        # Check if we have source data
        print("\n📋 Checking source data...")
        
        # Check teams
        cur.execute('SELECT COUNT(*) FROM "NBA"."Teams";')
        team_count = cur.fetchone()[0]
        print(f"  Teams: {team_count} records")
        
        # Check players
        cur.execute('SELECT COUNT(*) FROM "NBA"."Players";')
        player_count = cur.fetchone()[0]
        print(f"  Players: {player_count} records")
        
        # Check schedule
        cur.execute('SELECT COUNT(*) FROM "NBA"."Schedule";')
        schedule_count = cur.fetchone()[0]
        print(f"  Schedule: {schedule_count} records")
        
        conn.commit()
        conn.close()
        
        print("\n🎯 Next Steps:")
        if team_count > 0 or player_count > 0 or schedule_count > 0:
            print("1. Run the Streamlit app: streamlit run pages/Hybrid_Predict.py")
            print("2. Click '🧠 Create Vector Embeddings' in the sidebar")
            print("3. This will populate the embedding tables with vector data")
        else:
            print("1. First import some data (teams, players, or schedule)")
            print("2. Then create embeddings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_database()
