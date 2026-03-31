@echo off
echo ===== Simple pgvector Installation =====
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

REM Set paths
set PG_PATH=C:\Program Files\PostgreSQL\17
set PG_SERVICE=postgresql-x64-17
set DB_NAME=James
set DB_USER=postgres

REM Step 1: Check for existing files
echo Step 1: Checking for existing pgvector files...
echo.

if exist "%PG_PATH%\lib\vector.dll" (
    echo [OK] vector.dll already exists
) else (
    echo [MISSING] vector.dll not found
)

if exist "%PG_PATH%\share\extension\vector.control" (
    echo [OK] vector.control already exists
) else (
    echo [MISSING] vector.control not found
)

if exist "%PG_PATH%\share\extension\vector.sql" (
    echo [OK] vector.sql already exists
) else (
    echo [MISSING] vector.sql not found
)

echo.
echo Do you want to continue with installation? (Y/N)
set /p CONTINUE=
if /i "%CONTINUE%" NEQ "Y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

REM Step 2: Get ZIP file path
echo.
echo Step 2: Provide the pgvector ZIP file
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

REM Step 3: Extract files
echo.
echo Step 3: Extracting files...
echo.

REM Create a temporary directory
mkdir temp_pgvector 2>nul
cd temp_pgvector

REM Extract the ZIP file using built-in Windows commands
echo Extracting ZIP file...
echo. > extract.vbs
echo Set objShell = CreateObject("Shell.Application") >> extract.vbs
echo Set objSource = objShell.NameSpace("%ZIP_PATH%").Items() >> extract.vbs
echo Set objTarget = objShell.NameSpace("%CD%") >> extract.vbs
echo objTarget.CopyHere objSource, 16 >> extract.vbs
cscript //nologo extract.vbs
del extract.vbs

REM Step 4: Copy files
echo.
echo Step 4: Copying files...
echo.

echo Copying vector.dll to %PG_PATH%\lib\
copy /Y vector.dll "%PG_PATH%\lib\" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.dll
    cd ..
    rmdir /s /q temp_pgvector
    pause
    exit /b 1
)

echo Copying vector.control to %PG_PATH%\share\extension\
copy /Y vector.control "%PG_PATH%\share\extension\" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.control
    cd ..
    rmdir /s /q temp_pgvector
    pause
    exit /b 1
)

echo Copying SQL files to %PG_PATH%\share\extension\
copy /Y vector*.sql "%PG_PATH%\share\extension\" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy SQL files
    cd ..
    rmdir /s /q temp_pgvector
    pause
    exit /b 1
)

REM Clean up
cd ..
rmdir /s /q temp_pgvector

REM Step 5: Restart PostgreSQL service
echo.
echo Step 5: Restarting PostgreSQL service...
echo.

echo Stopping %PG_SERVICE% service...
net stop "%PG_SERVICE%" 2>nul

echo Waiting for service to fully stop...
timeout /t 3 /nobreak > nul

echo Starting %PG_SERVICE% service...
net start "%PG_SERVICE%" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to start %PG_SERVICE% service.
    echo Please start it manually using services.msc
    pause
)

REM Step 6: Create the extension
echo.
echo Step 6: Creating pgvector extension...
echo.

set /p DB_PASSWORD="Enter your database password: "

echo Creating pgvector extension in database %DB_NAME%...
"%PG_PATH%\bin\psql.exe" -d %DB_NAME% -U %DB_USER% -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo.
echo Verifying installation...
"%PG_PATH%\bin\psql.exe" -d %DB_NAME% -U %DB_USER% -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

echo.
echo ===== Installation Complete! =====
echo.
echo If you see a row with 'vector' above, pgvector was installed successfully!
echo.
pause 