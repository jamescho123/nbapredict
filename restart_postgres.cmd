@echo off
echo ===== Restart PostgreSQL Service =====
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

REM PostgreSQL service name
set PG_SERVICE=postgresql-x64-17

echo Stopping PostgreSQL service (%PG_SERVICE%)...
net stop "%PG_SERVICE%"

echo Waiting for service to fully stop...
timeout /t 3 /nobreak > nul

echo Starting PostgreSQL service (%PG_SERVICE%)...
net start "%PG_SERVICE%"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to start PostgreSQL service.
    echo Please check if the service name is correct.
    echo You can find the correct service name in Services (Run → services.msc)
    pause
    exit /b 1
)

echo.
echo PostgreSQL service restarted successfully!
echo.
echo Next step: Create the pgvector extension in your database:
echo    1. Connect to your database
echo    2. Run: CREATE EXTENSION vector;
echo.
pause 