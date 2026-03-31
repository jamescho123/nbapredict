# Upload to Supabase Instructions

## Current Status
✓ All 18 tables exported successfully to SQL file
✗ NOT YET UPLOADED to Supabase

## Tables Exported (18 total):
1. MatchEmbeddings (0 rows)
2. MatchPlayer (0 rows)
3. Matches (1,179 rows)
4. News (7,293 rows)
5. PlayerEmbeddings (0 rows)
6. Players (50 rows)
7. Schedule (308 rows)
8. Season2024_25_News (763 rows)
9. Season2024_25_Results (24 rows)
10. Season2024_25_Schedule (24 rows)
11. TeamEmbeddings (0 rows)
12. TeamPlayer (11,603 rows)
13. Teams (85 rows)
14. Test2024_25 (2 rows)
15. VectorNews (3,594 rows) - Contains vector embeddings
16. entity (11 rows)
17. entity_mention (14 rows)
18. news (3 rows)

**Total rows: ~25,000 rows**

## Next Steps to Complete Connection

### Option 1: Upload via Supabase SQL Editor (Recommended)

1. **Open the SQL file:**
   - File: `nba_manual_export_20251024_201041.sql`
   - Open with text editor and copy all contents (Ctrl+A, Ctrl+C)

2. **Go to Supabase SQL Editor:**
   - URL: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new
   - Login with: jamescho@jumbosoft.com

3. **Paste and Execute:**
   - Paste the SQL content into the editor
   - Click "Run" to execute
   - Wait for completion (may take a few minutes due to data volume)

### Option 2: Upload in Batches (If file is too large)

If the SQL file is too large to paste at once, I can split it into smaller batches:

```bash
python split_sql_export.py
```

This will create multiple smaller SQL files that you can upload one by one.

### Option 3: Try Direct Connection (If network allows)

```bash
python test_supabase_connection.py
```

If this succeeds, then run:
```bash
python migrate_to_supabase.py
```

## After Upload - Verify Migration

Run this to confirm all tables and data are in Supabase:

```bash
python verify_supabase_migration.py
```

## Important Notes

⚠️ **Large Data:**
- VectorNews table has 3,594 vector embeddings
- TeamPlayer has 11,603 rows
- Total file size may be several MB

⚠️ **Vector Extension:**
- The SQL includes: `CREATE EXTENSION IF NOT EXISTS vector;`
- Supabase should have pgvector pre-installed
- If you get errors about vector type, enable it manually in Supabase

⚠️ **Execution Time:**
- Expect 2-5 minutes for complete upload
- Don't close browser during execution

