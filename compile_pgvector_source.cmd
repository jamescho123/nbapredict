@echo off
echo ===== Compile pgvector from Source =====
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
set PGVECTOR_DIR=%~dp0pgvector
set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools

REM Check if pgvector directory exists
if not exist "%PGVECTOR_DIR%" (
    echo Error: pgvector directory not found at %PGVECTOR_DIR%
    pause
    exit /b 1
)

REM Check if PostgreSQL directory exists
if not exist "%PG_PATH%" (
    echo Error: PostgreSQL directory %PG_PATH% does not exist.
    pause
    exit /b 1
)

REM Check if Visual Studio directory exists
if not exist "%VS_PATH%" (
    echo Error: Visual Studio directory %VS_PATH% does not exist.
    pause
    exit /b 1
)

REM Set up Visual Studio environment
echo Setting up Visual Studio environment...
call "%VS_PATH%\Common7\Tools\VsDevCmd.bat" -arch=x64

REM Set environment variables for compilation
echo Setting up environment for compilation...
set PATH=%PG_PATH%\bin;%PATH%
set USE_PGXS=1
set PGWIN_DEPS=%PG_PATH%

echo PATH=%PATH%
echo USE_PGXS=%USE_PGXS%
echo PGWIN_DEPS=%PGWIN_DEPS%

REM Navigate to pgvector directory
cd "%PGVECTOR_DIR%"
echo Current directory: %CD%

REM Check for nmake
where nmake >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: nmake not found.
    echo Please make sure Visual Studio Build Tools with C++ support is installed
    echo and the environment is set up correctly.
    pause
    exit /b 1
)

echo nmake found at:
where nmake

REM Compile pgvector
echo.
echo Compiling pgvector...
nmake /f Makefile.win

if %ERRORLEVEL% NEQ 0 (
    echo Error: Compilation failed.
    pause
    exit /b 1
)

echo Compilation successful!

REM Install the compiled files
echo.
echo Installing pgvector...

REM Create directories if they don't exist
if not exist "%PG_PATH%\lib" mkdir "%PG_PATH%\lib"
if not exist "%PG_PATH%\share\extension" mkdir "%PG_PATH%\share\extension"

REM Copy vector.dll
echo Copying vector.dll to %PG_PATH%\lib\
copy /Y "vector.dll" "%PG_PATH%\lib\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.dll
    pause
    exit /b 1
)

REM Copy vector.control
echo Copying vector.control to %PG_PATH%\share\extension\
copy /Y "vector.control" "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.control
    pause
    exit /b 1
)

REM Copy SQL files
echo Copying SQL files to %PG_PATH%\share\extension\
copy /Y "sql\*.sql" "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy SQL files
    pause
    exit /b 1
)

echo.
echo Installation complete!
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