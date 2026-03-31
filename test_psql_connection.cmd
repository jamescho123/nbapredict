@echo off
SET PGPASSWORD=VXUXqY9Uofg9ujoo

echo Testing psql installation...
psql --version

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [FAIL] psql not found in PATH
    echo.
    echo Install PostgreSQL client tools:
    echo https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
    echo.
    echo Or download psql binaries:
    echo https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)

echo.
echo Testing connection to Supabase...
echo.

psql -h db.mxnpfsiyaqqwdcokukij.supabase.co -p 5432 -d postgres -U postgres -c "SELECT version();"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [OK] Connection successful!
    echo ========================================
    echo.
    echo You can now import the database:
    echo   psql_import.cmd
    echo.
    echo Or manually:
    echo   SET PGPASSWORD=VXUXqY9Uofg9ujoo
    echo   psql -h db.mxnpfsiyaqqwdcokukij.supabase.co -p 5432 -d postgres -U postgres -f nba_manual_export_20251024_201041.sql
) else (
    echo.
    echo ========================================
    echo [FAIL] Connection failed!
    echo ========================================
    echo.
    echo Possible causes:
    echo 1. Network/firewall blocking port 5432
    echo 2. Supabase project paused or deleted
    echo 3. Invalid credentials
    echo.
    echo Check Supabase dashboard:
    echo https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij
)

SET PGPASSWORD=
echo.
pause

