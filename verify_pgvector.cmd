@echo off
echo ===== pgvector Installation Verification =====
echo.

REM Get PostgreSQL path
set /p PG_PATH="Enter your PostgreSQL installation path (e.g. C:\Program Files\PostgreSQL\17): "

if not exist "%PG_PATH%" (
    echo Error: PostgreSQL path %PG_PATH% does not exist.
    pause
    exit /b 1
)

REM Check for vector.dll
echo Checking for vector.dll...
if exist "%PG_PATH%\lib\vector.dll" (
    echo Found vector.dll at %PG_PATH%\lib\vector.dll
) else (
    echo Error: vector.dll not found at %PG_PATH%\lib\vector.dll
    echo pgvector is not properly installed.
    pause
    exit /b 1
)

REM Check for vector.control
echo Checking for vector.control...
if exist "%PG_PATH%\share\extension\vector.control" (
    echo Found vector.control at %PG_PATH%\share\extension\vector.control
) else (
    echo Error: vector.control not found at %PG_PATH%\share\extension\vector.control
    echo pgvector is not properly installed.
    pause
    exit /b 1
)

REM Check for vector.sql
echo Checking for vector.sql...
if exist "%PG_PATH%\share\extension\vector.sql" (
    echo Found vector.sql at %PG_PATH%\share\extension\vector.sql
) else (
    echo Error: vector.sql not found at %PG_PATH%\share\extension\vector.sql
    echo pgvector is not properly installed.
    pause
    exit /b 1
)

echo.
echo All pgvector files are present!
echo.
echo To complete the installation:
echo 1. Make sure you've restarted the PostgreSQL service
echo 2. Connect to your database and run:
echo    CREATE EXTENSION vector;
echo 3. Verify with:
echo    SELECT * FROM pg_extension WHERE extname = 'vector';
echo.
pause 