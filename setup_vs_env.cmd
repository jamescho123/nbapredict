@echo off
echo ===== Setting up Visual Studio Build Tools environment =====
echo.

REM Find Visual Studio installation path
set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools

if not exist "%VS_PATH%" (
    echo Error: Visual Studio Build Tools not found at %VS_PATH%
    pause
    exit /b 1
)

echo Found Visual Studio Build Tools at %VS_PATH%

REM Set up the environment using the Developer Command Prompt
call "%VS_PATH%\Common7\Tools\VsDevCmd.bat" -arch=x64

echo.
echo Environment set up successfully!
echo You can now compile pgvector using compile_pgvector.cmd
echo.
pause 