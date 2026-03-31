@echo off
echo ===== Create pgvector Extension =====
echo.

REM Set database connection info
set DB_NAME=James
set DB_USER=postgres
set /p DB_PASSWORD="Enter your database password: "

echo Creating pgvector extension in database %DB_NAME%...
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -d %DB_NAME% -U %DB_USER% -c "CREATE EXTENSION IF NOT EXISTS vector;"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to create pgvector extension.
    echo.
    echo This could be because:
    echo 1. The database name or username is incorrect
    echo 2. The password is incorrect
    echo 3. The pgvector files are not properly installed
    echo 4. PostgreSQL service is not running
    pause
    exit /b 1
)

echo.
echo Verifying extension installation...
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -d %DB_NAME% -U %DB_USER% -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

echo.
echo If you see a row with 'vector' above, the extension was installed successfully!
echo You can now use vector embeddings in your PostgreSQL database.
echo.
pause 