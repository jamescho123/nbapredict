# Upload Split SQL Files to Supabase

## ✓ Files Created Successfully!

Your database has been split into 3 manageable files:

1. **nba_export_part1_schema_and_setup.sql**
   - Size: 0.1 KB (2 lines)
   - Contains: Schema and pgvector extension setup
   - Very quick to upload

2. **nba_export_part2_table_structures.sql**
   - Size: 5.7 KB (197 lines)
   - Contains: CREATE TABLE statements for all 18 tables
   - Quick to upload

3. **nba_export_part3_data_inserts.sql**
   - Size: 44.9 MB (26,350 lines)
   - Contains: All INSERT statements (~25,000 rows of data)
   - Takes 2-5 minutes to upload

## Upload Steps

### Step 1: Open Supabase SQL Editor

Go to: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new

Login with: `jamescho@jumbosoft.com`

### Step 2: Upload Part 1 (Schema Setup)

1. Open `nba_export_part1_schema_and_setup.sql` in text editor
2. Copy all contents (Ctrl+A, Ctrl+C)
3. Paste into Supabase SQL Editor (Ctrl+V)
4. Click "RUN" button
5. Wait for success message

**Expected result:** Creates NBA schema and enables vector extension

### Step 3: Upload Part 2 (Table Structures)

1. **CLEAR the SQL Editor** (select all and delete previous SQL)
2. Open `nba_export_part2_table_structures.sql`
3. Copy all contents (Ctrl+A, Ctrl+C)
4. Paste into Supabase SQL Editor (Ctrl+V)
5. Click "RUN" button
6. Wait for success message

**Expected result:** Creates all 18 tables (MatchEmbeddings, MatchPlayer, Matches, News, etc.)

### Step 4: Upload Part 3 (Data)

1. **CLEAR the SQL Editor** (select all and delete previous SQL)
2. Open `nba_export_part3_data_inserts.sql`
3. Copy all contents (Ctrl+A, Ctrl+C)
4. Paste into Supabase SQL Editor (Ctrl+V)
5. Click "RUN" button
6. **Wait 2-5 minutes** for completion (this is the largest file)

**Expected result:** Inserts all ~25,000 rows of data

### Step 5: Verify Migration

After all parts are uploaded, verify the import:

```bash
python verify_supabase_migration.py
```

This will check:
- All 18 tables exist
- Row counts match your local database
- Data integrity

## Troubleshooting

### "Error: relation already exists"
- This means you ran a part twice
- It's usually safe to ignore for CREATE TABLE statements
- For data inserts, you may get duplicate key errors

### "Query timeout" on Part 3
If Part 3 times out:
1. Split it further manually:
   - Copy first half of INSERT statements
   - Run them
   - Then copy second half
   - Run them

### "Out of memory" in browser
- Close other browser tabs
- Try Chrome/Edge instead of Firefox
- Or split Part 3 into smaller chunks

### Can't paste large file
Some browsers have paste limits. Try:
- Different browser (Chrome usually works best)
- Smaller chunks (split Part 3 manually)

## What Each File Contains

### Part 1: Schema Setup
```sql
CREATE SCHEMA IF NOT EXISTS "NBA";
CREATE EXTENSION IF NOT EXISTS vector;
```

### Part 2: Table Structures
```sql
DROP TABLE IF EXISTS "NBA"."MatchEmbeddings" CASCADE;
CREATE TABLE "NBA"."MatchEmbeddings" (
  "GameID" integer NOT NULL,
  "Embedding" vector,
  ...
);
-- ... 17 more tables
```

### Part 3: Data Inserts
```sql
INSERT INTO "NBA"."Matches" (...) VALUES (...);
INSERT INTO "NBA"."News" (...) VALUES (...);
-- ... ~25,000 INSERT statements
```

## After Successful Upload

### Update Your Applications

```python
# Use db_config.py to switch between local and Supabase
from db_config import get_connection

# To use Supabase:
# $env:USE_SUPABASE="true"
# python your_app.py

conn = get_connection()
```

### Test Connection

```python
from db_config import DB_CONFIG
import psycopg2

# Will use Supabase when USE_SUPABASE=true
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM \"NBA\".\"Matches\";")
print(f"Matches count: {cursor.fetchone()[0]}")
conn.close()
```

## Summary

✓ Large file split into 3 manageable parts
✓ Part 1: Schema (instant)
✓ Part 2: Tables (< 1 minute)
✓ Part 3: Data (2-5 minutes)

**Total upload time: ~5-10 minutes**

Start uploading from Part 1!

