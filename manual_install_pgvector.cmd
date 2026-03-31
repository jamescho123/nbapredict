@echo off
echo ===== Manual pgvector Installation =====
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

REM Get ZIP file path
echo.
echo Please download the pgvector ZIP file from:
echo https://github.com/pgvector/pgvector/releases
echo.
set /p ZIP_PATH="Enter the full path to the downloaded ZIP file: "

if not exist "%ZIP_PATH%" (
    echo Error: ZIP file %ZIP_PATH% does not exist.
    pause
    exit /b 1
)

REM Create temp directory
set TEMP_DIR=%TEMP%\pgvector_install
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

echo Extracting ZIP file...
powershell -Command "& {Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%TEMP_DIR%' -Force}"

echo.
echo Copying files to PostgreSQL directories...

if exist "%TEMP_DIR%\vector.dll" (
    echo Copying vector.dll to %PG_PATH%\lib\
    copy /Y "%TEMP_DIR%\vector.dll" "%PG_PATH%\lib\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy vector.dll
        pause
        exit /b 1
    )
) else (
    echo Error: vector.dll not found in the ZIP file.
    pause
    exit /b 1
)

if exist "%TEMP_DIR%\vector.control" (
    echo Copying vector.control to %PG_PATH%\share\extension\
    copy /Y "%TEMP_DIR%\vector.control" "%PG_PATH%\share\extension\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy vector.control
        pause
        exit /b 1
    )
) else (
    echo Error: vector.control not found in the ZIP file.
    pause
    exit /b 1
)

echo Copying SQL files to %PG_PATH%\share\extension\
copy /Y "%TEMP_DIR%\vector*.sql" "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy SQL files
    pause
    exit /b 1
)

echo Cleaning up...
rmdir /s /q "%TEMP_DIR%"

echo.
echo pgvector files installed successfully!
echo.
echo Next steps:
echo 1. Restart the PostgreSQL service using restart_postgres.cmd
echo 2. Connect to your database and run:
echo    CREATE EXTENSION vector;
echo 3. Verify with:
echo    SELECT * FROM pg_extension WHERE extname = 'vector';
echo.
pause 