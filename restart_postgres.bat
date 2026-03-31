@echo off
echo ===== PostgreSQL Service Restart Script =====

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

REM Find PostgreSQL service name
echo Searching for PostgreSQL service...
for /f "tokens=1,2* delims= " %%a in ('sc query state^= all ^| find /i "postgresql"') do (
    if "%%a"=="SERVICE_NAME:" (
        set PG_SERVICE=%%b
        echo Found PostgreSQL service: %%b
        goto :FOUND_SERVICE
    )
)

REM If not found by "postgresql", try with "pgsql"
for /f "tokens=1,2* delims= " %%a in ('sc query state^= all ^| find /i "pgsql"') do (
    if "%%a"=="SERVICE_NAME:" (
        set PG_SERVICE=%%b
        echo Found PostgreSQL service: %%b
        goto :FOUND_SERVICE
    )
)

echo Error: PostgreSQL service not found.
echo Please make sure PostgreSQL is installed as a service.
pause
exit /b 1

:FOUND_SERVICE
echo Stopping PostgreSQL service %PG_SERVICE%...
net stop %PG_SERVICE%

if %ERRORLEVEL% neq 0 (
    echo Error: Failed to stop PostgreSQL service.
    echo This might be because the service is already stopped or due to insufficient permissions.
    pause
    exit /b 1
)

echo PostgreSQL service stopped successfully.
echo Starting PostgreSQL service %PG_SERVICE%...
net start %PG_SERVICE%

if %ERRORLEVEL% neq 0 (
    echo Error: Failed to start PostgreSQL service.
    echo Please check the PostgreSQL error logs for details.
    pause
    exit /b 1
)

echo PostgreSQL service started successfully.
echo.
echo Next steps:
echo 1. Connect to your database and run: CREATE EXTENSION vector;
echo 2. Run check_pgvector.py to verify installation

pause 