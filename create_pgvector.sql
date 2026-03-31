-- Create the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Check if the extension was created successfully
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Add the embedding column to the News table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'NBA'
        AND table_name = 'News'
        AND column_name = 'Embedding'
    ) THEN
        ALTER TABLE "NBA"."News" ADD COLUMN "Embedding" vector(1024);
        RAISE NOTICE 'Added Embedding column to News table';
    ELSE
        RAISE NOTICE 'Embedding column already exists in News table';
    END IF;
END $$;

-- Try to create HNSW index (faster but requires newer PostgreSQL)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'NBA'
        AND tablename = 'News'
        AND indexname = 'news_embedding_hnsw_idx'
    ) THEN
        BEGIN
            CREATE INDEX news_embedding_hnsw_idx
            ON "NBA"."News" 
            USING hnsw ("Embedding" vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
            RAISE NOTICE 'Created HNSW index on Embedding column';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create HNSW index: %', SQLERRM;
            
            -- Try IVF index instead
            BEGIN
                CREATE INDEX news_embedding_ivf_idx
                ON "NBA"."News" 
                USING ivfflat ("Embedding" vector_cosine_ops)
                WITH (lists = 100);
                RAISE NOTICE 'Created IVF index on Embedding column';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Could not create IVF index: %', SQLERRM;
                RAISE NOTICE 'Continuing without index. Searches will be slower.';
            END;
        END;
    ELSE
        RAISE NOTICE 'Index already exists on Embedding column';
    END IF;
END $$; 