# Migration Instructions: Local PostgreSQL → Supabase

## Issue
Direct database connection to Supabase is blocked due to network/firewall restrictions.

## Solution: SQL Export Method

### Step 1: Export Local Database to SQL

Run the export script:
```cmd
python export_all_tables_to_sql.py
```

This creates a file: `nba_full_export_YYYYMMDD_HHMMSS.sql`

### Step 2: Upload to Supabase via SQL Editor

1. **Open Supabase SQL Editor:**
   - Go to: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new
   - Login with: jamescho@jumbosoft.com

2. **Execute the SQL file:**

   **Option A: Small Files (< 1MB)**
   - Open the generated SQL file
   - Copy all contents
   - Paste into Supabase SQL Editor
   - Click "Run"

   **Option B: Large Files (split into batches)**
   ```cmd
   python split_large_sql.py nba_full_export_YYYYMMDD_HHMMSS.sql
   ```
   This creates multiple files (part1.sql, part2.sql, etc.)
   - Execute each file separately in SQL Editor

### Step 3: Verify Migration

After uploading, verify the data:
```cmd
python verify_migration.py
```

This requires network access. If blocked, verify in Supabase SQL Editor:
```sql
SELECT 
    schemaname,
    tablename,
    (SELECT COUNT(*) FROM "NBA"."tablename") as row_count
FROM pg_tables 
WHERE schemaname = 'NBA'
ORDER BY tablename;
```

## Alternative: Single Table Sync

If you need to sync individual tables:
```cmd
python sync_single_table.py Teams
python sync_single_table.py Players
```

## Tools Created

1. **migrate_local_to_supabase.py** - Direct migration (requires network)
2. **export_all_tables_to_sql.py** - Export to SQL file (recommended)
3. **sync_single_table.py** - Sync one table (requires network)
4. **verify_migration.py** - Verify sync status (requires network)

## Network Troubleshooting

If network issues persist:

1. **Check Firewall:**
   - Allow outbound connections to *.supabase.co
   - Port 5432 (direct) or 6543 (pooler)

2. **Check Supabase Settings:**
   - Project Settings → Database → Connection Pooling
   - Ensure "Enable Pooler" is checked
   - Check IP whitelist settings

3. **Use VPN/Different Network:**
   - Corporate networks may block database connections
   - Try from different network or use VPN

## Recommended Approach

✓ **Use SQL Export Method** (export_all_tables_to_sql.py)
- Works regardless of network restrictions
- Can be executed in Supabase web interface
- Most reliable for initial migration

For ongoing sync after initial migration, resolve network issues for direct connection.

