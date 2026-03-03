import psycopg2
import logging

def create_entity_schema():
    """Create the PostgreSQL schema for NBA news entity extraction"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create entity type enum
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE entity_type AS ENUM (
                    'player', 'team', 'game', 'injury', 'conflict',
                    'stat', 'penalty', 'trade', 'award', 'location', 'date'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # Create news table (if not exists)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "NBA"."news" (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title TEXT,
                body TEXT,
                url TEXT,
                published_at TIMESTAMPTZ,
                source TEXT,
                created_at TIMESTAMPTZ DEFAULT now()
            )
        """)
        
        # Create entity table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "NBA"."entity" (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                etype entity_type NOT NULL,
                name TEXT NOT NULL,
                props JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ DEFAULT now(),
                UNIQUE(etype, name)
            )
        """)
        
        # Create entity_mention table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "NBA"."entity_mention" (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                news_id UUID REFERENCES "NBA"."news"(id) ON DELETE CASCADE,
                entity_id UUID REFERENCES "NBA"."entity"(id) ON DELETE CASCADE,
                details JSONB DEFAULT '{}'::jsonb,
                source TEXT NOT NULL DEFAULT 'llm',
                created_at TIMESTAMPTZ DEFAULT now()
            )
        """)
        
        # Create indexes for better performance
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_entity_type_name 
            ON "NBA"."entity" (etype, name)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_entity_mention_news_id 
            ON "NBA"."entity_mention" (news_id)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_entity_mention_entity_id 
            ON "NBA"."entity_mention" (entity_id)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_published_at 
            ON "NBA"."news" (published_at)
        """)
        
        # Create GIN index for JSONB details
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_entity_mention_details_gin 
            ON "NBA"."entity_mention" USING GIN (details)
        """)
        
        print("Entity extraction schema created successfully!")
        
    except Exception as e:
        print(f"Error creating entity schema: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_entity_schema()
