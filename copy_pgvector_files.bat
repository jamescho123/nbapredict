@echo off
echo ===== Copy pgvector Files =====
echo.
REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

REM Set paths
set PG_PATH=C:\Program Files\PostgreSQL\17
set VECTOR_DLL=C:\Users\hp\OneDrive\ÎÄµµ\GitHub\nbapredict\pgvector\vector.dll
set PGVECTOR_DIR=C:\Users\hp\OneDrive\ÎÄµµ\GitHub\nbapredict\pgvector

REM Create directories if they don't exist
if not exist "%PG_PATH%\lib" mkdir "%PG_PATH%\lib"
if not exist "%PG_PATH%\share\extension" mkdir "%PG_PATH%\share\extension"

REM Copy vector.dll
echo Copying vector.dll to %PG_PATH%\lib\
copy /Y "%VECTOR_DLL%" "%PG_PATH%\lib\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.dll
    pause
    exit /b 1
)

REM Copy vector.control
echo Copying vector.control to %PG_PATH%\share\extension\
copy /Y "%PGVECTOR_DIR%\vector.control" "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.control
    pause
    exit /b 1
)

REM Copy SQL files
echo Copying SQL files to %PG_PATH%\share\extension\
copy /Y "%PGVECTOR_DIR%\sql\*.sql" "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy SQL files
    pause
    exit /b 1
)

echo.
echo Files copied successfully!
echo.
echo Next steps:
echo 1. Restart PostgreSQL service:
echo    - Open Services (Run ¡ú services.msc)
echo    - Find postgresql-x64-17
echo    - Right-click and select "Restart"
echo.
echo 2. Connect to your database and run:
echo    CREATE EXTENSION vector;
echo.
pause
