@echo off
echo ===== Check pgvector Files =====
echo.

REM Set PostgreSQL path directly
set PG_PATH=C:\Program Files\PostgreSQL\17

echo Checking for vector.dll...
if exist "%PG_PATH%\lib\vector.dll" (
    echo [OK] Found vector.dll at %PG_PATH%\lib\vector.dll
) else (
    echo [MISSING] vector.dll not found at %PG_PATH%\lib\vector.dll
    echo This file is required for pgvector to work.
)

echo.
echo Checking for vector.control...
if exist "%PG_PATH%\share\extension\vector.control" (
    echo [OK] Found vector.control at %PG_PATH%\share\extension\vector.control
) else (
    echo [MISSING] vector.control not found at %PG_PATH%\share\extension\vector.control
    echo This file is required for pgvector to work.
)

echo.
echo Checking for vector.sql...
if exist "%PG_PATH%\share\extension\vector.sql" (
    echo [OK] Found vector.sql at %PG_PATH%\share\extension\vector.sql
) else (
    echo [MISSING] vector.sql not found at %PG_PATH%\share\extension\vector.sql
    echo This file is required for pgvector to work.
)

echo.
echo Checking for version upgrade SQL files...
dir "%PG_PATH%\share\extension\vector--*.sql" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [MISSING] No version upgrade SQL files found
) else (
    echo [OK] Version upgrade SQL files found
)

echo.
if exist "%PG_PATH%\lib\vector.dll" (
    if exist "%PG_PATH%\share\extension\vector.control" (
        if exist "%PG_PATH%\share\extension\vector.sql" (
            echo All required pgvector files are present!
            echo.
            echo Next steps:
            echo 1. Restart PostgreSQL service using restart_postgres.cmd
            echo 2. Create the extension using simple_create_extension.cmd
        ) else (
            echo Some pgvector files are missing!
        )
    ) else (
        echo Some pgvector files are missing!
    )
) else (
    echo Some pgvector files are missing!
)
echo.
pause 