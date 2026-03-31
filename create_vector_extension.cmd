@echo off
echo ===== Create Vector Extension =====
echo.

REM Set database connection info
set DB_NAME=James
set DB_USER=postgres
set /p DB_PASSWORD="Enter your database password: "

echo Creating vector extension in database %DB_NAME%...
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -d %DB_NAME% -U %DB_USER% -c "CREATE EXTENSION IF NOT EXISTS vector;"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to create vector extension.
    echo.
    echo This could be because:
    echo 1. The vector.dll file is not installed
    echo 2. PostgreSQL service was not restarted after installing vector.dll
    echo 3. Database credentials are incorrect
    echo.
    echo Please make sure:
    echo 1. vector.dll is in C:\Program Files\PostgreSQL\17\lib\
    echo 2. PostgreSQL service has been restarted
    echo 3. Database credentials are correct
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