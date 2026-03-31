@echo off
echo ===== Install vector.dll =====
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

REM Create temp directory
set TEMP_DIR=%TEMP%\pgvector_install
echo Creating temporary directory...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
cd "%TEMP_DIR%"

REM Download the file using PowerShell
echo Downloading pgvector ZIP file...
echo This may take a moment...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/pgvector/pgvector/releases/download/v0.8.0/vector-0.8.0-pg17-windows-x86_64.zip' -OutFile 'pgvector.zip'}"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to download pgvector ZIP file.
    cd ..
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM Extract ZIP file
echo Extracting ZIP file...
powershell -Command "& {Expand-Archive -Path 'pgvector.zip' -DestinationPath '.' -Force}"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to extract ZIP file.
    cd ..
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM Copy vector.dll
echo Copying vector.dll to PostgreSQL lib directory...
copy /Y "vector.dll" "C:\Program Files\PostgreSQL\17\lib\"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.dll.
    echo This could be because:
    echo 1. The file does not exist in the extracted ZIP
    echo 2. You don't have permission to write to the PostgreSQL directory
    cd ..
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM Clean up
cd ..
rmdir /s /q "%TEMP_DIR%"

echo.
echo vector.dll installed successfully!
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