@echo off
echo ===== Check PostgreSQL Service =====
echo.

echo Checking if PostgreSQL service is running...
sc query postgresql-x64-17 | findstr "STATE"

echo.
echo If you see "STATE : 4 RUNNING", the service is running.
echo If not, the service is not running or has a different name.
echo.

echo Listing all PostgreSQL services:
sc query state= all | findstr /i "postgresql"

echo.
echo The correct service name should be used in restart_postgres.cmd
echo.
pause 