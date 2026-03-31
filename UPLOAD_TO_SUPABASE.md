# Upload NBA Database to Supabase - Instructions

## ✓ Export Complete!

Your database has been exported to SQL files:

**Files Created:**
- `nba_full_export_20251027_173827_part1.sql` (10 MB)
- `nba_full_export_20251027_173827_part2.sql` (10 MB)
- `nba_full_export_20251027_173827_part3.sql` (10 MB)
- `nba_full_export_20251027_173827_part4.sql` (10 MB)
- `nba_full_export_20251027_173827_part5.sql` (10 MB)
- `nba_full_export_20251027_173827_part6.sql` (7.4 MB)

**Total Data:**
- 18 tables
- 24,953 rows

---

## Upload Steps

### 1. Open Supabase SQL Editor

Go to: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new

Login with: jamescho@jumbosoft.com

### 2. Execute Each Part in Order

**IMPORTANT:** Execute files in order (part1, part2, part3, etc.)

For each file:
1. Open the file in a text editor
2. Copy **ALL** contents (Ctrl+A, Ctrl+C)
3. Paste into Supabase SQL Editor
4. Click "Run" button
5. Wait for completion (you'll see "Success" message)
6. Move to next file

**File Order:**
1. `nba_full_export_20251027_173827_part1.sql`
2. `nba_full_export_20251027_173827_part2.sql`
3. `nba_full_export_20251027_173827_part3.sql`
4. `nba_full_export_20251027_173827_part4.sql`
5. `nba_full_export_20251027_173827_part5.sql`
6. `nba_full_export_20251027_173827_part6.sql`

### 3. Verify Upload

After uploading all parts, run this query in Supabase SQL Editor:

```sql
SELECT 
    table_name,
    (xpath('/row/cnt/text()', xml_count))[1]::text::int as row_count
FROM (
    SELECT 
        table_name,
        query_to_xml(
            format('SELECT COUNT(*) as cnt FROM "NBA".%I', table_name),
            false, true, ''
        ) as xml_count
    FROM information_schema.tables
    WHERE table_schema = 'NBA'
    ORDER BY table_name
) t;
```

Expected row counts:
- Matches: 1,179
- News: 7,293
- Players: 50
- Schedule: 308
- Season2024_25_News: 763
- Season2024_25_Results: 24
- Season2024_25_Schedule: 24
- TeamPlayer: 11,603
- Teams: 85
- Test2024_25: 2
- VectorNews: 3,594
- entity: 11
- entity_mention: 14
- news: 3

---

## Alternative: Use Supabase CLI (If Network Access Available)

If you can resolve the network issues:

```cmd
python migrate_local_to_supabase.py
```

This will automatically migrate all tables.

---

## Troubleshooting

### Error: "Query timeout"
- The file might be too large
- Split that specific part further:
  ```cmd
  python split_large_sql.py nba_full_export_20251027_173827_part1.sql 5
  ```

### Error: "Syntax error"
- Check that you copied the entire file
- Make sure no characters were cut off
- Try executing smaller sections

### Error: "Table does not exist"
- Ensure the NBA schema exists in Supabase
- Run schema creation script first (nba_export_part1_schema_and_setup.sql)

---

## After Upload

Once uploaded, you can:

1. **Use MCP Server** to query both databases:
   ```cmd
   python run_mcp_server.cmd
   ```

2. **Verify sync** between local and Supabase:
   ```cmd
   python verify_migration.py
   ```
   (Requires network access)

3. **Update single tables** as needed:
   ```cmd
   python sync_single_table.py Teams
   ```

---

## Files Location

All SQL files are in: `C:\Users\hp\OneDrive\文档\GitHub\nbapredict\`

Look for files starting with `nba_full_export_20251027_173827_part`

