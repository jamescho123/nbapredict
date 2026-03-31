@echo off
echo ===================================================
echo NBA Database Migration: Local PostgreSQL to Supabase
echo ===================================================
echo.
echo This will copy ALL tables from local database to Supabase
echo WARNING: This will TRUNCATE existing Supabase tables!
echo.
pause
echo.
python migrate_local_to_supabase.py
echo.
pause

