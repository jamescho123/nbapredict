@echo off
TITLE NBA Data Auto-Update (Every 6 Hours)
ECHO ========================================================
ECHO      NBA PREDICTION: CONTINUOUS DATA UPDATE
ECHO ========================================================
ECHO.
ECHO This script runs the daily/weekly data extraction process.
ECHO Please do not close this window until it finishes.
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

:: Run the update script
ECHO Starting continuous update process (every 6 hours)...
python continuous_data_update.py

ECHO.
ECHO ========================================================
IF %ERRORLEVEL% EQU 0 (
    ECHO Update completed successfully!
) ELSE (
    ECHO Update failed with errors. Check the output above.
)
ECHO ========================================================
ECHO.
ECHO This window will close in 60 seconds...
TIMEOUT /T 60
