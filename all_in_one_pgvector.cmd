@echo off
echo ===== All-in-One pgvector Installation =====
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

if not exist "%PG_PATH%" (
    echo Error: PostgreSQL path %PG_PATH% does not exist.
    pause
    exit /b 1
)

REM Step 1: Ask for the ZIP file path
echo Step 1: Provide the pgvector ZIP file
echo.
echo Please download the pgvector ZIP file from:
echo https://github.com/pgvector/pgvector/releases/tag/v0.8.0
echo File name: vector-0.8.0-pg17-windows-x86_64.zip
echo.
set /p ZIP_PATH="Enter the full path to the downloaded ZIP file: "

if not exist "%ZIP_PATH%" (
    echo Error: ZIP file %ZIP_PATH% does not exist.
    pause
    exit /b 1
)

REM Step 2: Extract and copy files
echo.
echo Step 2: Installing pgvector files
echo.

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

REM Step 3: Restart PostgreSQL service
echo.
echo Step 3: Restarting PostgreSQL service
echo.

set PG_SERVICE=postgresql-x64-17

echo Using PostgreSQL service name: %PG_SERVICE%
echo.

REM Stop the service
echo Stopping %PG_SERVICE% service...
net stop "%PG_SERVICE%"

if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to stop %PG_SERVICE% service.
    echo This could be because:
    echo 1. The service name is incorrect
    echo 2. The service is already stopped
    echo 3. You don't have permission to stop the service
    echo.
    echo Trying to start the service anyway...
) else (
    echo Service stopped successfully.
)

REM Wait a moment
echo Waiting for service to fully stop...
timeout /t 3 /nobreak > nul

REM Start the service
echo Starting %PG_SERVICE% service...
net start "%PG_SERVICE%"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to start %PG_SERVICE% service.
    echo Please try to start it manually:
    echo 1. Open Services (Run → services.msc)
    echo 2. Find the PostgreSQL service
    echo 3. Right-click and select "Start"
    pause
    exit /b 1
)

echo PostgreSQL service restarted successfully!

REM Step 4: Create the extension
echo.
echo Step 4: Creating pgvector extension
echo.

REM Set database connection info
set DB_NAME=James
set DB_USER=postgres
set /p DB_PASSWORD="Enter your database password: "

echo Creating pgvector extension in database %DB_NAME%...
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -d %DB_NAME% -U %DB_USER% -c "CREATE EXTENSION IF NOT EXISTS vector;"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to create pgvector extension.
    echo This could be because:
    echo 1. The database name or username is incorrect
    echo 2. The password is incorrect
    echo 3. The pgvector files are not properly installed
    echo 4. PostgreSQL service is not running
    pause
    exit /b 1
)

echo.
echo Verifying extension installation...
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -d %DB_NAME% -U %DB_USER% -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

echo.
echo ===== Installation Complete! =====
echo.
echo If you see a row with 'vector' above, pgvector was installed successfully!
echo You can now use vector embeddings in your PostgreSQL database.
echo.
pause 