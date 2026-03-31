@echo off
echo ===== Direct pgvector Download and Installation =====
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

REM Create temp directory
set TEMP_DIR=%TEMP%\pgvector_download
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
cd "%TEMP_DIR%"

echo Downloading pgvector binary using direct URL...
echo Please wait, this may take a moment...

REM Direct download URL for PostgreSQL 17
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/pgvector/pgvector/releases/download/v0.8.0/vector-0.8.0-pg17-windows-x86_64.zip' -OutFile 'pgvector.zip'}"

if not exist pgvector.zip (
    echo Error: Failed to download pgvector binary.
    echo.
    echo Please follow these manual steps:
    echo 1. Go to https://github.com/pgvector/pgvector/releases/tag/v0.8.0
    echo 2. Download vector-0.8.0-pg17-windows-x86_64.zip
    echo 3. Run manual_install_pgvector.cmd with the downloaded file
    echo.
    pause
    exit /b 1
)

echo Extracting files...
powershell -Command "& {Expand-Archive -Path 'pgvector.zip' -DestinationPath '.' -Force}"

echo Copying files to PostgreSQL directories...
copy /Y vector.dll "%PG_PATH%\lib\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.dll
    pause
    exit /b 1
)

copy /Y vector.control "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.control
    pause
    exit /b 1
)

copy /Y vector*.sql "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy SQL files
    pause
    exit /b 1
)

echo Cleaning up...
cd ..
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