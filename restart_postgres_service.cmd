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

REM Set the PostgreSQL service name
set PG_SERVICE=postgresql-x64-17

echo Using PostgreSQL service name: %PG_SERVICE%
echo.

REM Stop the service
echo Stopping %PG_SERVICE% service...
net stop "%PG_SERVICE%"

if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to stop %PG_SERVICE% service.
    echo This could be because:
    echo 1. The service name is incorrect
    echo 2. The service is already stopped
    echo 3. You don't have permission to stop the service
    echo.
    echo Trying to start the service anyway...
) else (
    echo Service stopped successfully.
)

REM Wait a moment
echo Waiting for service to fully stop...
timeout /t 3 /nobreak > nul

REM Start the service
echo Starting %PG_SERVICE% service...
net start "%PG_SERVICE%"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to start %PG_SERVICE% service.
    echo Please try to start it manually:
    echo 1. Open Services (Run → services.msc)
    echo 2. Find the PostgreSQL service
    echo 3. Right-click and select "Start"
    pause
    exit /b 1
)

echo.
echo PostgreSQL service restarted successfully!
echo.
echo Next step: Run create_vector_extension.cmd to create the pgvector extension
echo.
pause 