@echo off
echo ============================================================
echo Supabase MCP Setup for Cursor
echo ============================================================
echo.

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Download the LTS version and install it.
    echo.
    pause
    exit /b 1
)

node --version
echo [OK] Node.js is installed
echo.

REM Install Supabase MCP Server
echo Installing Supabase MCP Server...
echo.
npm install -g @modelcontextprotocol/server-supabase

if %errorLevel% equ 0 (
    echo.
    echo [OK] Supabase MCP Server installed successfully!
    echo.
) else (
    echo.
    echo [FAIL] Installation failed
    echo.
    echo Try running as Administrator or use:
    echo   npx @modelcontextprotocol/server-supabase
    echo.
)

echo ============================================================
echo Next Steps:
echo ============================================================
echo.
echo 1. Get your Supabase service_role key:
echo    https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/api
echo.
echo 2. Configure Cursor:
echo    - Press Ctrl+Shift+P
echo    - Type "Preferences: Open User Settings (JSON)"
echo    - Add MCP configuration (see SUPABASE_MCP_SETUP.md)
echo.
echo 3. Restart Cursor
echo.
echo 4. Test with: @supabase List all tables
echo.
echo See SUPABASE_MCP_SETUP.md for complete instructions
echo.
pause

