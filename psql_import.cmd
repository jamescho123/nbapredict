@echo off
REM Direct psql import to Supabase
REM Set password as environment variable

SET PGPASSWORD=VXUXqY9Uofg9ujoo

echo ========================================
echo Importing NBA Database to Supabase
echo ========================================
echo.
echo Host: db.mxnpfsiyaqqwdcokukij.supabase.co
echo Database: postgres
echo User: postgres
echo File: nba_manual_export_20251024_201041.sql
echo.
echo This may take 2-5 minutes...
echo.

psql -h db.mxnpfsiyaqqwdcokukij.supabase.co -p 5432 -d postgres -U postgres -f nba_manual_export_20251024_201041.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [OK] Import completed successfully!
    echo ========================================
    echo.
    echo Verify the migration:
    echo python verify_supabase_migration.py
) else (
    echo.
    echo ========================================
    echo [FAIL] Import failed!
    echo ========================================
    echo.
    echo Troubleshooting:
    echo 1. Check psql is installed: psql --version
    echo 2. Verify network connection
    echo 3. Check Supabase dashboard for errors
)

SET PGPASSWORD=
echo.
pause

