# Install psql (PostgreSQL Client) on Windows

## psql is NOT installed on your system

You need to install PostgreSQL client tools to use psql.

## Option 1: Install PostgreSQL (Recommended)

1. **Download PostgreSQL installer:**
   - URL: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Select latest version for Windows x86-64

2. **Run installer:**
   - You can choose "Command Line Tools Only" if you don't need the full server
   - Or install full PostgreSQL (you already have local PostgreSQL, so this adds psql to PATH)

3. **Add to PATH (if not automatic):**
   - Default location: `C:\Program Files\PostgreSQL\16\bin`
   - Add to System Environment Variables > PATH

4. **Verify installation:**
   ```cmd
   psql --version
   ```

## Option 2: Use Python Script (No psql needed)

Since you already have Python and psycopg2, use the direct migration script:

```cmd
python migrate_to_supabase.py
```

This bypasses psql and directly connects from PostgreSQL to Supabase.

## Option 3: Download psql Binaries Only

1. **Download PostgreSQL binaries:**
   - URL: https://www.enterprisedb.com/download-postgresql-binaries
   
2. **Extract and add to PATH:**
   - Extract to: `C:\PostgreSQL\bin`
   - Add `C:\PostgreSQL\bin` to PATH

## After Installing psql

Run one of these:

```cmd
# Test connection
test_psql_connection.cmd

# Import database
psql_import.cmd
```

Or manually:
```cmd
SET PGPASSWORD=VXUXqY9Uofg9ujoo
psql -h db.mxnpfsiyaqqwdcokukij.supabase.co -p 5432 -d postgres -U postgres -f nba_manual_export_20251024_201041.sql
```

