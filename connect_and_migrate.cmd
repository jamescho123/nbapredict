@echo off
REM Set Supabase password
SET PGPASSWORD=VXUXqY9Uofg9ujoo

echo Testing psql connection to Supabase...
psql -h db.mxnpfsiyaqqwdcokukij.supabase.co -p 5432 -d postgres -U postgres -c "SELECT version();"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Connection successful!
    echo.
    echo Ready to import data. Run:
    echo psql -h db.mxnpfsiyaqqwdcokukij.supabase.co -p 5432 -d postgres -U postgres -f nba_manual_export_20251024_201041.sql
    echo.
    choice /C YN /M "Import database now"
    if %ERRORLEVEL% EQU 1 (
        echo.
        echo Importing database...
        psql -h db.mxnpfsiyaqqwdcokukij.supabase.co -p 5432 -d postgres -U postgres -f nba_manual_export_20251024_201041.sql
        echo.
        echo Import complete! Run verify_supabase_migration.py to check.
    )
) else (
    echo.
    echo [FAIL] Connection failed!
    echo.
    echo Possible issues:
    echo 1. psql not installed or not in PATH
    echo 2. Network/firewall blocking connection
    echo 3. Incorrect credentials
    echo.
    echo Install PostgreSQL client tools from:
    echo https://www.postgresql.org/download/windows/
)

SET PGPASSWORD=
pause

