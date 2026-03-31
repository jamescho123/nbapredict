@echo off
echo ===== Install pgvector from master.zip =====
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
set ZIP_PATH=C:\Users\hp\Downloads\pgvector-master.zip
set TEMP_DIR=%TEMP%\pgvector_install

REM Create temp directory
echo Creating temporary directory...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
cd "%TEMP_DIR%"

REM Extract ZIP file
echo Extracting ZIP file...
powershell -Command "& {Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '.' -Force}"

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to extract ZIP file.
    cd ..
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM This is a source code package, so we need to compile it
echo.
echo This is a source code package. We need to compile it.
echo.

REM Check if Visual Studio Build Tools are installed
where nmake >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: nmake not found. Visual Studio Build Tools with C++ workload is required.
    echo Please install Visual Studio Build Tools from:
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    cd ..
    rmdir /s /q "%TEMP_DIR%"
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
        cd ..
        rmdir /s /q "%TEMP_DIR%"
        pause
        exit /b 1
    )
)

REM Navigate to the source directory
cd pgvector-master

REM Build pgvector
echo Building pgvector...
nmake /f Makefile.win

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build pgvector.
    cd ..\..
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM Copy files to PostgreSQL directories
echo Copying files to PostgreSQL directories...

REM Create directories if they don't exist
if not exist "%PG_PATH%\lib" mkdir "%PG_PATH%\lib"
if not exist "%PG_PATH%\share\extension" mkdir "%PG_PATH%\share\extension"

REM Copy vector.dll
echo Copying vector.dll to %PG_PATH%\lib\
copy /Y "vector.dll" "%PG_PATH%\lib\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.dll
    cd ..\..
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM Copy control file
echo Copying vector.control to %PG_PATH%\share\extension\
copy /Y "vector.control" "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy vector.control
    cd ..\..
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM Copy SQL files
echo Copying SQL files to %PG_PATH%\share\extension\
copy /Y "sql\*.sql" "%PG_PATH%\share\extension\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to copy SQL files
    cd ..\..
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM Clean up
cd ..\..
rmdir /s /q "%TEMP_DIR%"

echo.
echo pgvector files installed successfully!
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