-- Check if pgvector is available
SELECT * FROM pg_available_extensions WHERE name = 'vector';

-- Create the pgvector extension if available
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