@echo off
echo ===== Direct PostgreSQL Connection Test =====
echo.

REM Set database connection info with password directly in script
set DB_NAME=postgres
set DB_USER=postgres
set PGPASSWORD=jcjc1749

echo Testing connection with hardcoded password...
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -d %DB_NAME% -U %DB_USER% -c "SELECT version();"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to connect to PostgreSQL.
    echo This could be because:
    echo 1. The password is incorrect
    echo 2. PostgreSQL service is not running
    echo 3. The PostgreSQL path is incorrect
) else (
    echo.
    echo Connection successful!
    echo.
    echo Now trying to create pgvector extension...
    echo.
    
    "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -d James -U %DB_USER% -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Error: Failed to create pgvector extension.
        echo This could be because:
        echo 1. The database 'James' does not exist
        echo 2. The pgvector files are not properly installed
    ) else (
        echo.
        echo Successfully created pgvector extension!
        echo.
        echo Verifying installation:
        "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -d James -U %DB_USER% -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
    )
)

REM Clear password from environment
set PGPASSWORD=

echo.
pause 