# Supabase Connection Setup

## Database Credentials

**Supabase Project:**
- Project ID: mxnpfsiyaqqwdcokukij
- URL: https://mxnpfsiyaqqwdcokukij.supabase.co
- Database Password: VXUXqY9Uofg9ujoo

## Migration Options

### Option 1: Manual SQL Export (Recommended - Works without network issues)

1. **Export local database:**
```bash
python manual_export.py
```
This creates a file: `nba_manual_export_YYYYMMDD_HHMMSS.sql`

2. **Upload to Supabase:**
   - Open Supabase SQL Editor: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new
   - Copy contents of the generated SQL file
   - Paste into SQL Editor and execute

### Option 2: Direct Migration Script (Requires network access)

1. **Test connection first:**
```bash
python test_supabase_connection.py
```

2. **Run migration if connection succeeds:**
```bash
python migrate_to_supabase.py
```

### Option 3: PostgreSQL pg_dump (If pg_dump is installed)

```bash
python export_to_sql.py
```

Then upload the generated SQL file using psql or Supabase SQL Editor.

## Application Connection Strings

### Direct Connection (for server-side apps)
```python
import psycopg2

conn = psycopg2.connect(
    host='db.mxnpfsiyaqqwdcokukij.supabase.co',
    database='postgres',
    user='postgres',
    password='VXUXqY9Uofg9ujoo',
    port=5432
)
```

### Connection Pooler (recommended for serverless/high concurrency)
```python
import psycopg2

conn = psycopg2.connect(
    host='mxnpfsiyaqqwdcokukij.supabase.co',
    database='postgres',
    user='postgres.mxnpfsiyaqqwdcokukij',
    password='VXUXqY9Uofg9ujoo',
    port=6543
)
```

## Update Existing Code

Create a configuration file to switch between local and Supabase:

```python
# config.py
import os

USE_SUPABASE = os.getenv('USE_SUPABASE', 'false').lower() == 'true'

if USE_SUPABASE:
    DB_CONFIG = {
        'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'VXUXqY9Uofg9ujoo',
        'port': 5432
    }
else:
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'James',
        'user': 'postgres',
        'password': 'jcjc1749'
    }
```

## Verify Migration

After uploading, verify the data:

```bash
python verify_supabase_migration.py
```

## Troubleshooting

If you get network errors:
1. Check internet connection
2. Verify IP is allowed in Supabase Network settings
3. Use Option 1 (Manual SQL Export) instead

If SQL execution fails:
- Execute in smaller batches
- Check for large vector data that might need chunking
- Verify pgvector extension is enabled

