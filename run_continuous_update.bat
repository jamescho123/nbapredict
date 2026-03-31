@echo off
TITLE NBA Data Auto-Update (Every 6 Hours)
ECHO ========================================================
ECHO      NBA PREDICTION: CONTINUOUS DATA UPDATE
ECHO      Running every 6 hours while window is open
ECHO ========================================================
ECHO.

cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO ERROR: Python is not found in your PATH.
    ECHO Please install Python or add it to your PATH.
    PAUSE
    EXIT /B 1
)

:: Run the continuous update script
python continuous_data_update.py

PAUSE
