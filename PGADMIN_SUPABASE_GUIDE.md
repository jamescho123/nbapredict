# Connect PostgreSQL to Supabase using pgAdmin 4

## Perfect! You can use pgAdmin 4 to connect and migrate

Since you have pgAdmin 4 and PostgreSQL 17, you can directly connect to Supabase and import the database.

## Step 1: Add Supabase Server to pgAdmin 4

1. **Open pgAdmin 4**

2. **Right-click on "Servers" → "Register" → "Server"**

3. **General Tab:**
   - Name: `Supabase - NBA_Predict`
   - (or any name you prefer)

4. **Connection Tab:**
   - Host name/address: `aws-1-ap-southeast-1.pooler.supabase.com`
   - Port: `5432`
   - Maintenance database: `postgres`
   - Username: `postgres.mxnpfsiyaqqwdcokukij`
   - Password: `Jcjc1749!!!!`
   - ✓ Save password (optional, for convenience)

5. **Advanced Tab (Optional):**
   - DB restriction: `postgres` (to only show this database)

6. **SSL Tab (Important for Supabase):**
   - SSL mode: `Require` or `Prefer`

7. **Click "Save"**

## Step 2: Test Connection

If the connection succeeds, you'll see:
- Supabase server appear in the left panel
- Expand: `Supabase - NBA_Predict` → `Databases` → `postgres`

**If connection fails:**
- Your network is blocking port 5432
- Try using the connection pooler instead (see Option B below)

## Step 3: Import Database using pgAdmin 4

### Option A: Execute SQL File

1. **In pgAdmin, select your Supabase server:**
   - Expand: `Servers` → `Supabase - NBA_Predict` → `Databases` → `postgres`
   - Right-click on `postgres` → `Query Tool`

2. **Open SQL File:**
   - Click `File` icon (📁) → `Open File`
   - Navigate to: `nba_manual_export_20251024_201041.sql`
   - Click `Open`

3. **Execute:**
   - Click `Execute` (▶️ play button) or press `F5`
   - Wait 2-5 minutes for completion
   - Check "Messages" tab for progress

4. **Verify:**
   - Refresh the database tree (right-click `postgres` → `Refresh`)
   - Expand: `Schemas` → `NBA` → `Tables`
   - You should see all 18 tables

### Option B: Execute in Chunks (if file is too large)

If pgAdmin times out with the full file:

1. **Split the file first:**
   ```bash
   python split_sql_file.py
   ```

2. **Execute each part:**
   - First: `nba_export_part1_schema_and_setup.sql`
   - Then: `nba_export_part2_table_structures.sql`
   - Finally: `nba_export_part3_data_inserts.sql`

## Step 4: Verify Import

### Method 1: Using pgAdmin

1. **Check Tables:**
   - Expand: `Schemas` → `NBA` → `Tables`
   - You should see 18 tables

2. **Check Row Counts:**
   - Right-click on a table (e.g., `Matches`)
   - Select `View/Edit Data` → `First 100 Rows`
   - Or use Query Tool:
   ```sql
   SELECT 
       table_name,
       (SELECT COUNT(*) FROM "NBA"."Matches") as matches_count,
       (SELECT COUNT(*) FROM "NBA"."News") as news_count,
       (SELECT COUNT(*) FROM "NBA"."TeamPlayer") as teamplayer_count
   FROM information_schema.tables 
   WHERE table_schema = 'NBA' 
   LIMIT 1;
   ```

### Method 2: Using Python Script

```bash
python verify_supabase_migration.py
```

## Alternative: Connection Pooler (if direct connection blocked)

If port 5432 is blocked, try the connection pooler:

**Connection Tab:**
- Host name/address: `aws-1-ap-southeast-1.pooler.supabase.com`
- Port: `6543` ← Transaction pooler port
- Maintenance database: `postgres`
- Username: `postgres.mxnpfsiyaqqwdcokukij` ← Different username format
- Password: `Jcjc1749!!!!`

## Bonus: Copy Database Between Servers in pgAdmin

You can also use pgAdmin's built-in backup/restore:

### From Local PostgreSQL to Supabase:

1. **Backup Local Database:**
   - Right-click on local `James` database
   - `Backup...`
   - Format: `Custom` or `Plain`
   - Filename: `nba_backup.backup`
   - Sections: Check `Data`, `Pre-data`, `Post-data`
   - Click `Backup`

2. **Restore to Supabase:**
   - Connect to Supabase server (as described in Step 1)
   - Right-click on `postgres` database
   - `Restore...`
   - Filename: `nba_backup.backup`
   - Click `Restore`

**Note:** This method may have issues with the NBA schema. The SQL file method is more reliable.

## Troubleshooting

### Error: "Connection timed out"
- Your network is blocking PostgreSQL ports
- Solutions:
  1. Try connection pooler (port 6543)
  2. Use Supabase web interface instead
  3. Contact IT to whitelist `*.supabase.co` ports 5432, 6543

### Error: "could not translate host name"
- DNS issue
- Solutions:
  1. Flush DNS: `ipconfig /flushdns`
  2. Use Google DNS (8.8.8.8)
  3. Try IPv6 address from nslookup

### Error: "password authentication failed"
- Double-check password: `VXUXqY9Uofg9ujoo`
- Verify in Supabase dashboard

### Error: "SSL required"
- Go to SSL tab in server connection
- Set SSL mode to: `Require`

### SQL Execution Timeout
- Split the SQL file: `python split_sql_file.py`
- Execute parts separately
- Or increase pgAdmin timeout: File → Preferences → Query Tool → Query execution → Query Tool command timeout

## After Successful Import

### Switch Your Applications to Use Supabase:

```python
# Use db_config.py
from db_config import get_connection

# To use Supabase:
$env:USE_SUPABASE="true"
python your_script.py

# Or directly in your code:
import psycopg2
conn = psycopg2.connect(
    host='db.mxnpfsiyaqqwdcokukij.supabase.co',
    database='postgres',
    user='postgres',
    password='VXUXqY9Uofg9ujoo',
    port=5432
)
```

### Keep Both Local and Supabase

You now have:
- **Local:** For development and testing
- **Supabase:** For production/cloud access

Use `db_config.py` to easily switch between them!

## Summary

✓ Add Supabase server to pgAdmin 4
✓ Open Query Tool
✓ Load `nba_manual_export_20251024_201041.sql`
✓ Execute (F5)
✓ Verify tables in NBA schema
✓ Done!

