@echo off
echo ===== pgvector DLL Copy Script =====

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

REM Check if PostgreSQL path is provided
if "%1"=="" (
    set /p PG_PATH="Enter PostgreSQL installation path (e.g. C:\Program Files\PostgreSQL\17): "
) else (
    set PG_PATH=%1
)

REM Verify PostgreSQL path exists
if not exist "%PG_PATH%" (
    echo Error: PostgreSQL path %PG_PATH% does not exist.
    pause
    exit /b 1
)

REM Verify PostgreSQL lib directory exists
if not exist "%PG_PATH%\lib" (
    echo Error: PostgreSQL lib directory not found at %PG_PATH%\lib
    pause
    exit /b 1
)

echo PostgreSQL installation found at: %PG_PATH%

REM Check if the DLL already exists
if exist "%PG_PATH%\lib\vector.dll" (
    echo vector.dll already exists in %PG_PATH%\lib
    set /p OVERWRITE="Do you want to overwrite it? (y/n): "
    if /i "%OVERWRITE%"=="y" (
        echo Will overwrite existing vector.dll
    ) else (
        echo Operation cancelled.
        pause
        exit /b 0
    )
)

REM Download the pre-compiled DLL from GitHub
echo Downloading pre-compiled pgvector DLL...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/pgvector/pgvector/releases/download/v0.8.0/vector-0.8.0-pg17-windows-x86_64.zip' -OutFile 'pgvector.zip'}"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to download pgvector DLL.
    echo Trying alternative download method...
    
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/pgvector/pgvector/releases/download/v0.8.0/vector-0.8.0-pg17-windows-x86_64.zip' -OutFile 'pgvector.zip'}"
    
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to download pgvector DLL using alternative method.
        echo Please download the DLL manually from:
        echo https://github.com/pgvector/pgvector/releases/download/v0.8.0/vector-0.8.0-pg17-windows-x86_64.zip
        pause
        exit /b 1
    )
)

REM Extract the ZIP file
echo Extracting pgvector.zip...
powershell -Command "& {Expand-Archive -Path 'pgvector.zip' -DestinationPath 'pgvector_tmp' -Force}"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to extract pgvector.zip.
    pause
    exit /b 1
)

REM Copy the DLL to the PostgreSQL lib directory
echo Copying vector.dll to %PG_PATH%\lib...
if exist "pgvector_tmp\vector.dll" (
    copy /Y "pgvector_tmp\vector.dll" "%PG_PATH%\lib\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy vector.dll to %PG_PATH%\lib
        pause
        exit /b 1
    )
) else (
    echo Error: vector.dll not found in extracted files.
    pause
    exit /b 1
)

REM Copy the SQL and control files to the PostgreSQL share\extension directory
echo Copying SQL and control files to %PG_PATH%\share\extension...
if exist "pgvector_tmp\vector.control" (
    copy /Y "pgvector_tmp\vector.control" "%PG_PATH%\share\extension\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy vector.control to %PG_PATH%\share\extension
        pause
        exit /b 1
    )
)

if exist "pgvector_tmp\vector.sql" (
    copy /Y "pgvector_tmp\vector.sql" "%PG_PATH%\share\extension\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy vector.sql to %PG_PATH%\share\extension
        pause
        exit /b 1
    )
)

for %%f in (pgvector_tmp\vector--*.sql) do (
    copy /Y "%%f" "%PG_PATH%\share\extension\"
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to copy %%f to %PG_PATH%\share\extension
        pause
        exit /b 1
    )
)

REM Clean up
echo Cleaning up temporary files...
rmdir /S /Q pgvector_tmp
del pgvector.zip

echo Installation complete!
echo.
echo Next steps:
echo 1. Restart the PostgreSQL service using restart_postgres.bat
echo 2. Connect to your database and run: CREATE EXTENSION vector;
echo 3. Run check_pgvector.py to verify installation

pause 