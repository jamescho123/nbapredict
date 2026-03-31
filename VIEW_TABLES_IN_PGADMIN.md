# How to View Tables in pgAdmin

## Issue: Can't See Tables in Supabase

The tables exist but may not be visible in pgAdmin. Follow these steps:

## Step 1: Refresh the Database

1. **In pgAdmin, right-click on `postgres` database**
2. **Select `Refresh`**
3. Wait for the refresh to complete

## Step 2: Navigate to NBA Schema

1. **Expand the database tree:**
   ```
   Servers
   └── Supabase - NBA
       └── Databases
           └── postgres
               └── Schemas
                   └── NBA  ← Click here to expand
                       └── Tables  ← Your tables are here
   ```

2. **If you don't see "Schemas":**
   - Right-click `postgres` → `Refresh`
   - Expand `postgres` → Look for `Schemas` folder

## Step 3: View Tables

Once you expand `Schemas` → `NBA` → `Tables`, you should see:
- MatchEmbeddings
- MatchPlayer
- Matches
- News
- PlayerEmbeddings
- Players
- Schedule
- Season2024_25_News
- Season2024_25_Results
- Season2024_25_Schedule
- TeamEmbeddings
- TeamPlayer
- Teams
- Test2024_25
- VectorNews
- entity
- entity_mention
- news

## Step 4: Verify Tables Have Data

**Current Status:** All tables exist but are **EMPTY** (0 rows)

To populate them, you need to import the data:

### Option A: Import SQL File via pgAdmin

1. **Right-click `postgres` → `Query Tool`**
2. **File → Open File**
3. **Select:** `nba_export_for_pgadmin_20251113_200558.sql`
4. **Click Execute (F5)**
5. **Wait 2-5 minutes for completion**

### Option B: Use Migration Script

```bash
python migrate_local_to_supabase.py
```

## Step 5: Check Table Data

After importing, verify data:

1. **Right-click a table (e.g., `Teams`)**
2. **Select `View/Edit Data` → `First 100 Rows`**
3. You should see data

Or use Query Tool:
```sql
SELECT COUNT(*) FROM "NBA"."Teams";
SELECT COUNT(*) FROM "NBA"."Players";
SELECT COUNT(*) FROM "NBA"."Matches";
```

## Troubleshooting

### "I don't see the Schemas folder"

**Solution:**
- Right-click `postgres` → `Refresh`
- Make sure you're connected to the correct database
- Check connection settings

### "I see Schemas but not NBA"

**Solution:**
- The NBA schema exists (verified)
- Try: Right-click `Schemas` → `Refresh`
- Or run this query in Query Tool:
  ```sql
  SELECT schema_name 
  FROM information_schema.schemata 
  WHERE schema_name = 'NBA';
  ```

### "I see NBA schema but no Tables"

**Solution:**
- Right-click `NBA` → `Refresh`
- Tables exist (18 tables verified)
- If still not visible, check permissions

### "Tables are empty"

**This is expected!** The tables exist but have no data yet.

**Next step:** Import the SQL file to populate data:
- File: `nba_export_for_pgadmin_20251113_200558.sql`
- Contains 29,585 rows of data

## Quick Verification Query

Run this in pgAdmin Query Tool to see all tables:

```sql
SELECT 
    table_schema,
    table_name,
    (SELECT COUNT(*) 
     FROM information_schema.columns 
     WHERE table_schema = t.table_schema 
     AND table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'NBA'
AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

This will show all 18 tables in the NBA schema.

## Summary

✓ **Tables exist:** 18 tables in NBA schema
✗ **Tables are empty:** Need to import data
✓ **Solution:** Import `nba_export_for_pgadmin_20251113_200558.sql` via Query Tool












