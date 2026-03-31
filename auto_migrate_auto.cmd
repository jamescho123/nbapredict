@echo off
echo ===================================================
echo NBA Database Automatic Migration
echo ===================================================
echo.
echo Automatically migrating ALL tables from
echo Local PostgreSQL to Supabase
echo.
echo This will TRUNCATE and REPLACE all data in Supabase!
echo.
pause
echo.
python auto_migrate_simple.py
echo.
pause

