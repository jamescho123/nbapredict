@echo off
echo ===== Copy vector.dll =====
echo.

echo This script will copy vector.dll to PostgreSQL lib directory.
echo.
echo Please download vector-0.8.0-pg17-windows-x86_64.zip from:
echo https://github.com/pgvector/pgvector/releases/tag/v0.8.0
echo.
echo Extract the ZIP file and note the location of vector.dll
echo.
set /p DLL_PATH="Enter the full path to vector.dll: "

if not exist "%DLL_PATH%" (
    echo Error: vector.dll not found at %DLL_PATH%
    pause
    exit /b 1
)

echo Copying vector.dll to C:\Program Files\PostgreSQL\17\lib\
copy /Y "%DLL_PATH%" "C:\Program Files\PostgreSQL\17\lib\"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.dll
    echo Please run this script as administrator.
    pause
    exit /b 1
)

echo.
echo vector.dll copied successfully!
echo.
echo Next steps:
echo 1. Restart PostgreSQL service:
echo    - Open Services (Run → services.msc)
echo    - Find postgresql-x64-17
echo    - Right-click and select "Restart"
echo.
echo 2. Connect to your database and run:
echo    CREATE EXTENSION vector;
echo.
pause 