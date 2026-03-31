# Supabase Migration Guide

## Current Situation

Your local PostgreSQL database has been successfully exported, but direct connection to Supabase is blocked by your network (firewall/proxy blocking ports 5432 and 6543).

## Database Overview

- **Local Database:** `James` schema `NBA`
- **Supabase Project:** mxnpfsiyaqqwdcokukij
- **Tables:** 18 tables with ~25,000 rows
- **Export File:** `nba_manual_export_20251024_201041.sql` (304,500 lines)

### Tables to Migrate:
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
15. VectorNews (3,594 rows with vector embeddings)
16. entity (11 rows)
17. entity_mention (14 rows)
18. news (3 rows)

## Migration Method: Web Interface Upload

Since PostgreSQL ports are blocked, use Supabase SQL Editor:

### Step 1: Access Supabase SQL Editor

```
https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new
```

Login with: `jamescho@jumbosoft.com`

### Step 2: Prepare SQL File

The file `nba_manual_export_20251024_201041.sql` is ready.

**Option A: Upload Entire File (if it works)**
1. Open `nba_manual_export_20251024_201041.sql` in text editor
2. Copy all contents (Ctrl+A, Ctrl+C)
3. Paste into Supabase SQL Editor (Ctrl+V)
4. Click "RUN"
5. Wait 2-5 minutes

**Option B: Split Into Smaller Files (if file is too large)**
```bash
python split_sql_file.py
```
This creates multiple smaller files that you upload one by one.

### Step 3: Verify Migration

```bash
python verify_supabase_migration.py
```

This will check:
- All tables exist
- Row counts match
- Data integrity

## Configuration Files Created

### `db_config.py`
Centralized database configuration that switches between local and Supabase:

```python
from db_config import get_connection

# Uses local by default
conn = get_connection()

# Use Supabase:
# $env:USE_SUPABASE="true"
# python your_script.py
```

### Connection Details

**Local PostgreSQL:**
```python
host = 'localhost'
database = 'James'
user = 'postgres'
password = 'jcjc1749'
schema = 'NBA'
```

**Supabase:**
```python
host = 'mxnpfsiyaqqwdcokukij.supabase.co'  # pooler
# or: 'db.mxnpfsiyaqqwdcokukij.supabase.co'  # direct
database = 'postgres'
user = 'postgres'  # or 'postgres.mxnpfsiyaqqwdcokukij' for pooler
password = 'VXUXqY9Uofg9ujoo'
port = 5432  # direct, or 6543 for pooler
schema = 'NBA'
```

## Scripts Available

### Testing & Diagnostics
- `diagnose_connection.py` - Diagnose network issues
- `check_export_status.py` - Check what was exported
- `use_connection_pooler.py` - Test Supabase connection

### Migration
- `manual_export.py` - Export local DB to SQL file ✓ DONE
- `migrate_to_supabase.py` - Direct migration (requires open ports)
- `split_sql_file.py` - Split large SQL file

### Verification
- `verify_supabase_migration.py` - Verify migration success

### Command Files (requires psql)
- `test_psql_connection.cmd` - Test psql connection
- `psql_import.cmd` - Import via psql
- `connect_and_migrate.cmd` - All-in-one migration

## Troubleshooting

### "Connection timed out" Error
- Your network blocks PostgreSQL ports
- Solution: Use web interface upload

### "File too large" in Web Interface
- Run: `python split_sql_file.py`
- Upload split files one by one

### Vector Extension Error
- Supabase usually has pgvector pre-installed
- If not, enable in: Project Settings > Extensions

### After Migration

1. **Update Application Code:**
```python
# Add to your scripts:
from db_config import get_connection
conn = get_connection()
```

2. **Switch to Supabase:**
```bash
$env:USE_SUPABASE="true"
python your_app.py
```

3. **Switch back to Local:**
```bash
$env:USE_SUPABASE="false"
python your_app.py
```

## Support

- Supabase Dashboard: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij
- Documentation: See `SUPABASE_SETUP.md`, `FINAL_SOLUTION.md`, `Database.md`

