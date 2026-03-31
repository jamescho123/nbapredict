# Fix: entity_type Error

## Problem
```
ERROR: 42704: type "entity_type" does not exist
LINE 174: "etype" entity_type NOT NULL,
```

## Cause
The `entity_type` is a custom ENUM type that wasn't included in Part 1 (schema setup).

## Solution - UPDATED FILE

✓ I've updated `nba_export_part1_schema_and_setup.sql` to include the missing type.

### Re-upload Part 1

1. **Clear the Supabase SQL Editor**

2. **Copy the UPDATED Part 1:**
   Open: `nba_export_part1_schema_and_setup.sql`
   
   It now contains:
   ```sql
   CREATE SCHEMA IF NOT EXISTS "NBA";
   CREATE EXTENSION IF NOT EXISTS vector;
   
   -- Custom enum type for entity table
   CREATE TYPE entity_type AS ENUM ('player', 'team', 'game', 'injury', 'conflict', 'stat', 'penalty', 'trade', 'award', 'location', 'date');
   ```

3. **Paste and RUN in Supabase**

4. **Now re-upload Part 2:**
   - Clear editor
   - Copy `nba_export_part2_table_structures.sql`
   - Paste and RUN
   - Should work now!

5. **Continue with Part 3:**
   - Copy `nba_export_part3_data_inserts.sql`
   - Paste and RUN

## Alternative: Manual Fix

If you already ran Part 1, you can just add the missing type:

In Supabase SQL Editor, run:
```sql
CREATE TYPE entity_type AS ENUM ('player', 'team', 'game', 'injury', 'conflict', 'stat', 'penalty', 'trade', 'award', 'location', 'date');
```

Then continue with Part 2.

## What is entity_type?

This is a custom PostgreSQL ENUM type used by the `entity` table to categorize different entity types in your NBA data:
- player
- team
- game
- injury
- conflict
- stat
- penalty
- trade
- award
- location
- date

