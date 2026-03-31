@echo off
echo ===== Compile pgvector from Source =====
echo.

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

REM Check if vector.dll was created
if not exist "vector.dll" (
    echo Error: vector.dll was not created during compilation.
    pause
    exit /b 1
)

echo.
echo vector.dll was successfully compiled!
echo.
echo Next steps:
echo 1. You need to copy the following files as administrator:
echo    - Copy %PGVECTOR_DIR%\vector.dll to %PG_PATH%\lib\
echo    - Copy %PGVECTOR_DIR%\vector.control to %PG_PATH%\share\extension\
echo    - Copy %PGVECTOR_DIR%\sql\*.sql to %PG_PATH%\share\extension\
echo.
echo 2. Restart PostgreSQL service:
echo    - Open Services (Run → services.msc)
echo    - Find postgresql-x64-17
echo    - Right-click and select "Restart"
echo.
echo 3. Connect to your database and run:
echo    CREATE EXTENSION vector;
echo.
echo Would you like to create a script to copy these files? (Y/N)
set /p CREATE_SCRIPT=

if /i "%CREATE_SCRIPT%" EQU "Y" (
    echo @echo off > copy_pgvector_files.cmd
    echo echo ===== Copy pgvector Files ===== >> copy_pgvector_files.cmd
    echo echo. >> copy_pgvector_files.cmd
    echo REM Check for admin privileges >> copy_pgvector_files.cmd
    echo net session ^>nul 2^>^&1 >> copy_pgvector_files.cmd
    echo if %%ERRORLEVEL%% NEQ 0 ^( >> copy_pgvector_files.cmd
    echo     echo Error: This script requires administrator privileges. >> copy_pgvector_files.cmd
    echo     echo Please right-click on this script and select "Run as administrator". >> copy_pgvector_files.cmd
    echo     pause >> copy_pgvector_files.cmd
    echo     exit /b 1 >> copy_pgvector_files.cmd
    echo ^) >> copy_pgvector_files.cmd
    echo. >> copy_pgvector_files.cmd
    echo REM Set paths >> copy_pgvector_files.cmd
    echo set PG_PATH=C:\Program Files\PostgreSQL\17 >> copy_pgvector_files.cmd
    echo set PGVECTOR_DIR=%PGVECTOR_DIR% >> copy_pgvector_files.cmd
    echo. >> copy_pgvector_files.cmd
    echo REM Create directories if they don't exist >> copy_pgvector_files.cmd
    echo if not exist "%%PG_PATH%%\lib" mkdir "%%PG_PATH%%\lib" >> copy_pgvector_files.cmd
    echo if not exist "%%PG_PATH%%\share\extension" mkdir "%%PG_PATH%%\share\extension" >> copy_pgvector_files.cmd
    echo. >> copy_pgvector_files.cmd
    echo REM Copy vector.dll >> copy_pgvector_files.cmd
    echo echo Copying vector.dll to %%PG_PATH%%\lib\ >> copy_pgvector_files.cmd
    echo copy /Y "%%PGVECTOR_DIR%%\vector.dll" "%%PG_PATH%%\lib\" >> copy_pgvector_files.cmd
    echo if %%ERRORLEVEL%% NEQ 0 ^( >> copy_pgvector_files.cmd
    echo     echo Error: Failed to copy vector.dll >> copy_pgvector_files.cmd
    echo     pause >> copy_pgvector_files.cmd
    echo     exit /b 1 >> copy_pgvector_files.cmd
    echo ^) >> copy_pgvector_files.cmd
    echo. >> copy_pgvector_files.cmd
    echo REM Copy vector.control >> copy_pgvector_files.cmd
    echo echo Copying vector.control to %%PG_PATH%%\share\extension\ >> copy_pgvector_files.cmd
    echo copy /Y "%%PGVECTOR_DIR%%\vector.control" "%%PG_PATH%%\share\extension\" >> copy_pgvector_files.cmd
    echo if %%ERRORLEVEL%% NEQ 0 ^( >> copy_pgvector_files.cmd
    echo     echo Error: Failed to copy vector.control >> copy_pgvector_files.cmd
    echo     pause >> copy_pgvector_files.cmd
    echo     exit /b 1 >> copy_pgvector_files.cmd
    echo ^) >> copy_pgvector_files.cmd
    echo. >> copy_pgvector_files.cmd
    echo REM Copy SQL files >> copy_pgvector_files.cmd
    echo echo Copying SQL files to %%PG_PATH%%\share\extension\ >> copy_pgvector_files.cmd
    echo copy /Y "%%PGVECTOR_DIR%%\sql\*.sql" "%%PG_PATH%%\share\extension\" >> copy_pgvector_files.cmd
    echo if %%ERRORLEVEL%% NEQ 0 ^( >> copy_pgvector_files.cmd
    echo     echo Error: Failed to copy SQL files >> copy_pgvector_files.cmd
    echo     pause >> copy_pgvector_files.cmd
    echo     exit /b 1 >> copy_pgvector_files.cmd
    echo ^) >> copy_pgvector_files.cmd
    echo. >> copy_pgvector_files.cmd
    echo echo. >> copy_pgvector_files.cmd
    echo echo Files copied successfully! >> copy_pgvector_files.cmd
    echo echo. >> copy_pgvector_files.cmd
    echo echo Next steps: >> copy_pgvector_files.cmd
    echo echo 1. Restart PostgreSQL service: >> copy_pgvector_files.cmd
    echo echo    - Open Services ^(Run ^→ services.msc^) >> copy_pgvector_files.cmd
    echo echo    - Find postgresql-x64-17 >> copy_pgvector_files.cmd
    echo echo    - Right-click and select "Restart" >> copy_pgvector_files.cmd
    echo echo. >> copy_pgvector_files.cmd
    echo echo 2. Connect to your database and run: >> copy_pgvector_files.cmd
    echo echo    CREATE EXTENSION vector; >> copy_pgvector_files.cmd
    echo echo. >> copy_pgvector_files.cmd
    echo pause >> copy_pgvector_files.cmd
    
    echo.
    echo Script created: copy_pgvector_files.cmd
    echo After compilation is complete, run this script as administrator to copy the files.
)

pause 