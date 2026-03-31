@echo off
echo Installing pgvector extension for PostgreSQL...

REM Set PostgreSQL path - change this to your PostgreSQL installation path
set PG_PATH=C:\Program Files\PostgreSQL\17

REM Check if PostgreSQL directory exists
if not exist "%PG_PATH%" (
    echo Error: PostgreSQL directory not found at %PG_PATH%
    echo Please edit this batch file and set the correct path.
    pause
    exit /b 1
)

REM Set source and destination paths
set PROJECT_DIR=%~dp0
set PGVECTOR_DIR=%PROJECT_DIR%pgvector
set PG_LIB_DIR=%PG_PATH%\lib
set PG_EXT_DIR=%PG_PATH%\share\extension
set SQL_DIR=%PGVECTOR_DIR%\sql

REM Check if source directories exist
if not exist "%PGVECTOR_DIR%" (
    echo Error: pgvector directory not found at %PGVECTOR_DIR%
    pause
    exit /b 1
)

if not exist "%SQL_DIR%" (
    echo Error: SQL directory not found at %SQL_DIR%
    pause
    exit /b 1
)

REM Check if destination directories exist
if not exist "%PG_LIB_DIR%" (
    echo Error: PostgreSQL lib directory not found at %PG_LIB_DIR%
    pause
    exit /b 1
)

if not exist "%PG_EXT_DIR%" (
    echo Error: PostgreSQL extension directory not found at %PG_EXT_DIR%
    pause
    exit /b 1
)

REM Copy vector.control to extension directory
echo Copying vector.control to %PG_EXT_DIR%...
copy /Y "%PGVECTOR_DIR%\vector.control" "%PG_EXT_DIR%"
if %ERRORLEVEL% neq 0 (
    echo Error copying vector.control
    pause
    exit /b 1
)

REM Copy vector.sql to extension directory
echo Copying vector.sql to %PG_EXT_DIR%...
copy /Y "%SQL_DIR%\vector.sql" "%PG_EXT_DIR%"
if %ERRORLEVEL% neq 0 (
    echo Error copying vector.sql
    pause
    exit /b 1
)

REM Copy all version upgrade SQL files
echo Copying version upgrade SQL files...
for %%f in ("%SQL_DIR%\vector--*.sql") do (
    echo Copying %%~nxf...
    copy /Y "%%f" "%PG_EXT_DIR%"
    if %ERRORLEVEL% neq 0 (
        echo Error copying %%~nxf
        pause
        exit /b 1
    )
)

echo.
echo Files copied successfully!
echo.
echo Next steps:
echo 1. Restart the PostgreSQL service
echo 2. Connect to your database and run: CREATE EXTENSION vector;
echo 3. Run check_pgvector.py to verify installation
echo.

pause 