@echo off
echo ===== Copy pgvector Files from Source =====
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

REM Get PostgreSQL path
set /p PG_PATH="Enter your PostgreSQL installation path (e.g. C:\Program Files\PostgreSQL\17): "

if not exist "%PG_PATH%" (
    echo Error: PostgreSQL path %PG_PATH% does not exist.
    pause
    exit /b 1
)

REM Get pgvector source path
set PGVECTOR_DIR=%~dp0pgvector
if not exist "%PGVECTOR_DIR%" (
    echo Error: pgvector directory not found at %PGVECTOR_DIR%
    echo Please make sure the pgvector directory is in the same directory as this script.
    pause
    exit /b 1
)

echo Found pgvector directory at %PGVECTOR_DIR%
echo.

echo Copying pgvector files to PostgreSQL directories...

REM Copy control file
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
echo Files copied successfully, but vector.dll is missing.
echo You need to either:
echo 1. Compile pgvector from source using compile_pgvector.cmd
echo 2. Download a pre-compiled binary from https://github.com/pgvector/pgvector/releases
echo.
echo Next steps:
echo 1. Get vector.dll and copy it to %PG_PATH%\lib\
echo 2. Restart the PostgreSQL service using restart_postgres.cmd
echo 3. Connect to your database and run:
echo    CREATE EXTENSION vector;
echo.
pause 