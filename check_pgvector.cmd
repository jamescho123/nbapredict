@echo off
echo ===== Check pgvector Installation =====
echo.

REM Set database connection info
set DB_NAME=James
set DB_USER=postgres
set /p DB_PASSWORD="Enter your database password: "

echo Checking pgvector files...
echo.

echo 1. Checking for vector.dll...
if exist "C:\Program Files\PostgreSQL\17\lib\vector.dll" (
    echo [OK] vector.dll found
) else (
    echo [MISSING] vector.dll not found
)

echo 2. Checking for vector.control...
if exist "C:\Program Files\PostgreSQL\17\share\extension\vector.control" (
    echo [OK] vector.control found
) else (
    echo [MISSING] vector.control not found
)

echo 3. Checking for SQL files...
if exist "C:\Program Files\PostgreSQL\17\share\extension\vector.sql" (
    echo [OK] vector.sql found
) else (
    echo [MISSING] vector.sql not found
)

echo.
echo Checking pgvector extension in database...
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -d %DB_NAME% -U %DB_USER% -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to check extension in database.
    echo This could be because:
    echo 1. The database name or username is incorrect
    echo 2. The password is incorrect
    echo 3. PostgreSQL service is not running
    echo.
) else (
    echo.
    echo If you see a row with 'vector' above, the extension is installed in your database.
    echo If no rows are returned, the extension is not installed.
    echo.
    echo To install the extension, run:
    echo CREATE EXTENSION vector;
)

echo.
pause 