@echo off
echo ===== Finding Visual Studio Installation =====
echo.

REM Check for possible Visual Studio installation paths
set VS_PATHS=0

if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools" (
    echo Found: C:\Program Files\Microsoft Visual Studio\2022\BuildTools
    set VS_PATHS=1
    set VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\BuildTools
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Community" (
    echo Found: C:\Program Files\Microsoft Visual Studio\2022\Community
    set VS_PATHS=1
    set VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional" (
    echo Found: C:\Program Files\Microsoft Visual Studio\2022\Professional
    set VS_PATHS=1
    set VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Enterprise" (
    echo Found: C:\Program Files\Microsoft Visual Studio\2022\Enterprise
    set VS_PATHS=1
    set VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Enterprise
)

if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools" (
    echo Found: C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools
    set VS_PATHS=1
    set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools
)

if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community" (
    echo Found: C:\Program Files (x86)\Microsoft Visual Studio\2019\Community
    set VS_PATHS=1
    set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community
)

if "%VS_PATHS%"=="0" (
    echo No Visual Studio installation found.
    echo Please install Visual Studio with C++ build tools.
    pause
    exit /b 1
)

echo.
echo Using Visual Studio at: %VS_PATH%
echo.

REM Try to set up the environment
echo Setting up Visual Studio environment...
if exist "%VS_PATH%\Common7\Tools\VsDevCmd.bat" (
    echo Found VsDevCmd.bat at %VS_PATH%\Common7\Tools\VsDevCmd.bat
    call "%VS_PATH%\Common7\Tools\VsDevCmd.bat" -arch=x64
) else (
    echo VsDevCmd.bat not found at %VS_PATH%\Common7\Tools\VsDevCmd.bat
    pause
    exit /b 1
)

REM Check if nmake is available now
where nmake
if %ERRORLEVEL% NEQ 0 (
    echo Error: nmake still not found after setting up the environment.
    echo Please make sure the C++ build tools are installed.
    pause
    exit /b 1
) else (
    echo nmake found successfully!
)

echo.
echo Visual Studio environment set up successfully!
echo You can now run compile_pgvector.cmd to compile pgvector.
echo.
pause 