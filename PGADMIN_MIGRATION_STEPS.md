# pgAdmin Migration: Local PostgreSQL 17 → Supabase

## Quick Steps

### Step 1: Export Local Database to SQL

```bash
python export_for_pgadmin.py
```

This creates: `nba_export_for_pgadmin_YYYYMMDD_HHMMSS.sql`

### Step 2: Connect pgAdmin to Supabase

1. **Open pgAdmin 4**

2. **Register Supabase Server:**
   - Right-click `Servers` → `Register` → `Server`

3. **General Tab:**
   - Name: `Supabase - NBA`

4. **Connection Tab:**
   - Host: `aws-1-ap-southeast-1.pooler.supabase.com`
   - Port: `5432`
   - Database: `postgres`
   - Username: `postgres.mxnpfsiyaqqwdcokukij`
   - Password: `Jcjc1749!!!!`
   - ✓ Save password

5. **SSL Tab:**
   - SSL mode: `Require`

6. **Click "Save"**

### Step 3: Import SQL File via pgAdmin

1. **In pgAdmin:**
   - Expand: `Servers` → `Supabase - NBA` → `Databases` → `postgres`
   - Right-click `postgres` → `Query Tool`

2. **Load SQL File:**
   - Click `File` icon (📁) → `Open File`
   - Select: `nba_export_for_pgadmin_YYYYMMDD_HHMMSS.sql`
   - Click `Open`

3. **Execute:**
   - Click `Execute` (▶️) or press `F5`
   - Wait for completion (2-5 minutes)
   - Check "Messages" tab for progress

### Step 4: Verify Import

1. **Refresh database:**
   - Right-click `postgres` → `Refresh`

2. **Check tables:**
   - Expand: `Schemas` → `NBA` → `Tables`
   - You should see all tables

3. **Verify row counts:**
   - Right-click a table → `View/Edit Data` → `First 100 Rows`

## Alternative: pgAdmin Backup/Restore Method

### Method A: Backup Local Database

1. **In pgAdmin, connect to local PostgreSQL 17:**
   - Right-click `James` database → `Backup...`

2. **Backup Options:**
   - Filename: `nba_local_backup.backup`
   - Format: `Custom` (recommended) or `Plain`
   - Sections:
     - ✓ Pre-data (schema, tables, etc.)
     - ✓ Data (table data)
     - ✓ Post-data (indexes, constraints, etc.)

3. **Click "Backup"**

### Method B: Restore to Supabase

1. **In pgAdmin, connect to Supabase:**
   - Right-click `postgres` database → `Restore...`

2. **Restore Options:**
   - Filename: `nba_local_backup.backup`
   - Format: `Custom` or `Plain` (match backup format)
   - Options:
     - ✓ Pre-data
     - ✓ Data
     - ✓ Post-data
     - Schema: `NBA` (if available)

3. **Click "Restore"**

**Note:** Backup/Restore may have issues with schema names. SQL file method is more reliable.

## Alternative: Copy Data Using pgAdmin Query Tool

### Copy Individual Tables

1. **Connect to both servers in pgAdmin:**
   - Local PostgreSQL 17 (James database)
   - Supabase (postgres database)

2. **For each table:**
   - Open Query Tool on local database
   - Run:
   ```sql
   COPY "NBA"."TableName" TO STDOUT WITH CSV HEADER;
   ```
   - Copy the output
   - Open Query Tool on Supabase
   - Run:
   ```sql
   COPY "NBA"."TableName" FROM STDIN WITH CSV HEADER;
   ```
   - Paste the data

### Bulk Copy All Tables

Use the SQL export method (Step 1-3) - it's easier and more reliable.

## Troubleshooting

### Connection Issues

**"Connection timed out"**
- Network blocking port 5432
- Try transaction pooler (port 6543):
  - Host: `aws-1-ap-southeast-1.pooler.supabase.com`
  - Port: `6543`
  - Username: `postgres.mxnpfsiyaqqwdcokukij`

**"could not translate host name"**
- DNS issue
- Try: `ipconfig /flushdns` in Command Prompt
- Or use Supabase web SQL Editor instead

**"SSL required"**
- Go to SSL tab in server connection
- Set SSL mode: `Require`

### Import Issues

**"File too large"**
- Split the SQL file:
  ```bash
  python split_sql_file.py nba_export_for_pgadmin_YYYYMMDD_HHMMSS.sql
  ```
- Execute parts separately

**"Query execution timeout"**
- Increase timeout: File → Preferences → Query Tool → Query execution → Query Tool command timeout
- Or split the file into smaller chunks

**"Schema NBA does not exist"**
- The SQL file includes `CREATE SCHEMA IF NOT EXISTS`
- If it still fails, manually create:
  ```sql
  CREATE SCHEMA "NBA";
  ```

## Connection Details Summary

### Local PostgreSQL 17
- Host: `localhost`
- Port: `5432`
- Database: `James`
- Username: `postgres`
- Password: `jcjc1749`
- Schema: `NBA`

### Supabase
- Host: `aws-1-ap-southeast-1.pooler.supabase.com`
- Port: `5432` (Session pooler) or `6543` (Transaction pooler)
- Database: `postgres`
- Username: `postgres.mxnpfsiyaqqwdcokukij` (required for pooler)
- Password: `Jcjc1749!!!!`
- Schema: `NBA`

## After Migration

### Verify Data

```sql
-- Check table counts
SELECT 
    table_name,
    (SELECT COUNT(*) FROM "NBA"."Teams") as teams_count,
    (SELECT COUNT(*) FROM "NBA"."Players") as players_count,
    (SELECT COUNT(*) FROM "NBA"."Matches") as matches_count
FROM information_schema.tables 
WHERE table_schema = 'NBA' 
LIMIT 1;
```

### Update Applications

Use `db_config.py` to switch to Supabase:

```python
# Set environment variable
$env:USE_SUPABASE="true"
python your_script.py
```

Or update connection directly in code.

## Summary

✓ Export local database: `python export_for_pgadmin.py`
✓ Connect pgAdmin to Supabase
✓ Open Query Tool on `postgres` database
✓ Load SQL file and execute (F5)
✓ Verify tables in NBA schema
✓ Done!

