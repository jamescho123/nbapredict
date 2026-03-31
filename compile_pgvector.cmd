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
set SRC_DIR=C:\Users\hp\Downloads\pgvector-master

REM Check if source directory exists
if not exist "%SRC_DIR%" (
    echo Error: Source directory %SRC_DIR% does not exist.
    echo Please extract pgvector-master.zip first.
    pause
    exit /b 1
)

REM Check for nmake
where nmake >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: nmake not found. Visual Studio Build Tools with C++ workload is required.
    echo Please install Visual Studio Build Tools from:
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    pause
    exit /b 1
)

REM Set up Visual Studio environment
echo Setting up Visual Studio environment...
call "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Could not find Visual Studio 2022. Trying 2019...
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Could not set up Visual Studio environment.
        echo Please make sure Visual Studio Build Tools are installed.
        pause
        exit /b 1
    )
)

REM Navigate to the source directory
cd /d "%SRC_DIR%"

REM Build pgvector
echo Building pgvector...
nmake /f Makefile.win

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build pgvector.
    pause
    exit /b 1
)

REM Copy files to PostgreSQL directories
echo.
echo Copying files to PostgreSQL directories...

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

REM Copy control file
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
echo pgvector compiled and installed successfully!
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