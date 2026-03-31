@echo off
setlocal enabledelayedexpansion

echo ===== pgvector Compilation Script for Windows =====

REM Check if PostgreSQL path is provided
if "%1"=="" (
    set /p PG_PATH="Enter PostgreSQL installation path (e.g. C:\Program Files\PostgreSQL\17): "
) else (
    set PG_PATH=%1
)

REM Verify PostgreSQL path exists
if not exist "%PG_PATH%" (
    echo Error: PostgreSQL path %PG_PATH% does not exist.
    exit /b 1
)

REM Verify PostgreSQL bin directory exists
if not exist "%PG_PATH%\bin" (
    echo Error: PostgreSQL bin directory not found at %PG_PATH%\bin
    exit /b 1
)

REM Check for pg_config
if not exist "%PG_PATH%\bin\pg_config.exe" (
    echo Error: pg_config.exe not found at %PG_PATH%\bin\pg_config.exe
    exit /b 1
)

echo PostgreSQL installation found at: %PG_PATH%

REM Check for pgvector source directory
set PGVECTOR_DIR=%~dp0pgvector
if not exist "%PGVECTOR_DIR%" (
    echo Error: pgvector directory not found at %PGVECTOR_DIR%
    exit /b 1
)

echo pgvector source directory found at: %PGVECTOR_DIR%

REM Check for Visual Studio build tools
where nmake >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: nmake not found. Make sure Visual Studio with C++ build tools is installed.
    echo You can download Visual Studio Build Tools from:
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    exit /b 1
)

echo Visual Studio build tools found.

REM Set environment variables for compilation
set PATH=%PG_PATH%\bin;%PATH%
set USE_PGXS=1
set PGWIN_DEPS=%PG_PATH%

echo Setting up environment for compilation:
echo PATH=%PATH%
echo USE_PGXS=%USE_PGXS%
echo PGWIN_DEPS=%PGWIN_DEPS%

REM Navigate to pgvector directory and compile
cd "%PGVECTOR_DIR%"
echo Current directory: %CD%

echo Running nmake...
nmake /f Makefile.win

if %ERRORLEVEL% NEQ 0 (
    echo Error: Compilation failed.
    exit /b 1
)

echo Compilation successful!

REM Install the compiled files
echo Installing pgvector...
nmake /f Makefile.win install

if %ERRORLEVEL% NEQ 0 (
    echo Error: Installation failed.
    echo Attempting to manually copy files...
    
    REM Try to manually copy the files
    if exist "vector.dll" (
        echo Copying vector.dll to %PG_PATH%\lib
        copy /Y "vector.dll" "%PG_PATH%\lib\"
    ) else (
        echo Error: vector.dll not found.
    )
    
    if exist "vector.control" (
        echo Copying vector.control to %PG_PATH%\share\extension
        copy /Y "vector.control" "%PG_PATH%\share\extension\"
    ) else (
        echo Error: vector.control not found.
    )
    
    if exist "vector.sql" (
        echo Copying vector.sql to %PG_PATH%\share\extension
        copy /Y "vector.sql" "%PG_PATH%\share\extension\"
    ) else (
        echo Error: vector.sql not found.
    )
    
    for %%f in (vector--*.sql) do (
        echo Copying %%f to %PG_PATH%\share\extension
        copy /Y "%%f" "%PG_PATH%\share\extension\"
    )
)

echo Installation complete!
echo.
echo Next steps:
echo 1. Restart the PostgreSQL service
echo 2. Connect to your database and run: CREATE EXTENSION vector;
echo 3. Run check_pgvector.py to verify installation

endlocal 