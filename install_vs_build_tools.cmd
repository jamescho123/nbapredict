@echo off
echo ===== Visual Studio Build Tools Installer =====
echo.
echo This script will download and install Visual Studio Build Tools with C++ support
echo which is required to compile pgvector.
echo.

set DOWNLOAD_URL=https://aka.ms/vs/17/release/vs_buildtools.exe
set INSTALLER=vs_buildtools.exe

echo Downloading Visual Studio Build Tools...
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALLER%'}"

if not exist %INSTALLER% (
    echo Failed to download the installer.
    echo Please download Visual Studio Build Tools manually from:
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    pause
    exit /b 1
)

echo Download complete.
echo.
echo Installing Visual Studio Build Tools with C++ support...
echo This may take some time. Please be patient.
echo.
echo When the installer opens:
echo 1. Select "Desktop development with C++"
echo 2. Click "Install"
echo 3. Wait for the installation to complete
echo 4. After installation, restart your computer
echo.
echo Press any key to start the installer...
pause > nul

start "" %INSTALLER% --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive

echo.
echo After installation completes, please restart your computer.
echo Then you can compile pgvector using the instructions in pgvector_installation_steps.md
echo.
pause 