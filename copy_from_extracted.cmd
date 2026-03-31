@echo off
echo ===== Copy pgvector Files from Extracted Directory =====
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

REM Set PostgreSQL path
set PG_PATH=C:\Program Files\PostgreSQL\17

REM Ask for the extracted directory path
echo Please enter the path to the extracted pgvector-master directory
echo Example: C:\Users\hp\Downloads\pgvector-master
echo.
set /p SRC_DIR="Enter path: "

if not exist "%SRC_DIR%" (
    echo Error: Directory %SRC_DIR% does not exist.
    pause
    exit /b 1
)

echo.
echo Copying files to PostgreSQL directories...
echo.

REM Copy control file
echo Copying vector.control to %PG_PATH%\share\extension\
if exist "%SRC_DIR%\vector.control" (
    copy /Y "%SRC_DIR%\vector.control" "%PG_PATH%\share\extension\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy vector.control
        pause
        exit /b 1
    )
) else (
    echo Warning: vector.control not found in %SRC_DIR%
)

REM Copy SQL files
echo Copying SQL files to %PG_PATH%\share\extension\
if exist "%SRC_DIR%\sql" (
    copy /Y "%SRC_DIR%\sql\*.sql" "%PG_PATH%\share\extension\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy SQL files
        pause
        exit /b 1
    )
) else (
    echo Warning: SQL directory not found in %SRC_DIR%
)

REM Check if vector.dll exists
if exist "%SRC_DIR%\vector.dll" (
    echo Copying vector.dll to %PG_PATH%\lib\
    copy /Y "%SRC_DIR%\vector.dll" "%PG_PATH%\lib\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy vector.dll
        pause
        exit /b 1
    )
) else (
    echo Warning: vector.dll not found in %SRC_DIR%
    echo This file needs to be compiled from source or downloaded separately.
)

echo.
echo Files copied successfully!
echo.
echo Next steps:
echo 1. If vector.dll was not found, you need to compile it or download a pre-built version.
echo 2. Restart PostgreSQL service:
echo    - Open Services (Run → services.msc)
echo    - Find postgresql-x64-17
echo    - Right-click and select "Restart"
echo 3. Connect to your database and run:
echo    CREATE EXTENSION vector;
echo.
pause 