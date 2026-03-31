@echo off
echo ===== Debug Visual Studio Path =====
echo.

set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools

echo Checking if Visual Studio exists at: %VS_PATH%
if exist "%VS_PATH%" (
    echo [OK] Visual Studio found at %VS_PATH%
) else (
    echo [ERROR] Visual Studio not found at %VS_PATH%
)

echo.
echo Checking for VsDevCmd.bat...
set VSDEVCMD=%VS_PATH%\Common7\Tools\VsDevCmd.bat
if exist "%VSDEVCMD%" (
    echo [OK] VsDevCmd.bat found at %VSDEVCMD%
) else (
    echo [ERROR] VsDevCmd.bat not found at %VSDEVCMD%
)

echo.
echo Searching for VsDevCmd.bat in the system...
where /r C:\ VsDevCmd.bat

echo.
echo Checking for nmake...
where nmake 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] nmake not found in PATH
) else (
    echo [OK] nmake found in PATH
)

echo.
echo Press any key to exit...
pause > nul 