@echo off
echo ===== Test PostgreSQL Connection =====
echo.

REM Set database connection info
set DB_NAME=postgres
set DB_USER=postgres
set /p DB_PASSWORD="Enter your database password: "

echo Testing connection to PostgreSQL...
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -d %DB_NAME% -U %DB_USER% -c "SELECT version();"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to connect to PostgreSQL.
    echo This could be because:
    echo 1. The password is incorrect
    echo 2. PostgreSQL service is not running
    echo 3. The PostgreSQL path is incorrect
    echo.
    echo Try connecting to the default 'postgres' database instead of your specific database.
) else (
    echo.
    echo Connection successful!
    echo.
    echo Now testing connection to your database (James)...
    echo.
    
    "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -d James -U %DB_USER% -c "SELECT current_database();"
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Error: Failed to connect to database 'James'.
        echo This could be because:
        echo 1. The database does not exist
        echo 2. The user does not have access to this database
    ) else (
        echo.
        echo Connection to database 'James' successful!
    )
)

echo.
pause 