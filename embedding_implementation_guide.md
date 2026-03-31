# NBA News Embedding Implementation Guide

## Overview

This guide explains how to implement the vector embedding system for NBA news articles in your PostgreSQL database. The system uses:

1. **pgvector extension**: For storing and querying vector embeddings in PostgreSQL
2. **Ollama**: For generating embeddings using the bge-m3 model
3. **news_embedding.py**: Script to process news articles and generate embeddings

## Step 1: Install pgvector Extension

You need to install the pgvector extension on your PostgreSQL server:

```sql
-- Run as superuser
CREATE EXTENSION vector;
```

## Step 2: Add Embedding Column to News Table

Add a vector column to your News table:

```sql
ALTER TABLE "NBA"."News" ADD COLUMN "Embedding" vector(1024);
```

## Step 3: Install Ollama

1. Download and install Ollama from: https://ollama.com/
2. Start the Ollama service
3. Pull the bge-m3 model:
```
ollama pull bge-m3
```

## Step 4: Run the Embedding Script

Run the news_embedding.py script to process your news articles:

```
python news_embedding.py
```

This will:
1. Check if pgvector is installed
2. Add the Embedding column if needed
3. Process all news articles without embeddings
4. Generate and store embeddings for each article

## Vector Format

The embeddings are 1024-dimensional vectors:

- **Raw format**: Python list with 1024 float values
- **Database storage**: PostgreSQL vector type (pgvector)
- **Example values**: [-0.18, -0.03, 0.20, 0.73, -0.31, ...]
- **Value range**: Typically between -1 and 1

## Searching Similar News

Once embeddings are generated, you can search for similar news using:

```python
results = search_similar_news("NBA playoffs")
```

This will:
1. Generate an embedding for the query text
2. Find news articles with similar embeddings using cosine similarity
3. Return the most relevant articles

## Troubleshooting

1. **pgvector not found**: Make sure the extension is installed on your PostgreSQL server
2. **Ollama connection error**: Ensure Ollama service is running on localhost:11434
3. **Model not found**: Run `ollama pull bge-m3` to download the model
4. **Database connection error**: Check your PostgreSQL credentials and connection 