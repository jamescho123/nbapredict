@echo off
echo ===================================================
echo NBA Database Automatic Migration via MCP
echo ===================================================
echo.
echo This will automatically migrate ALL tables from
echo Local PostgreSQL to Supabase using MCP.
echo.
echo Requirements:
echo - Network access to Supabase
echo - MCP server dependencies installed (run setup_mcp.cmd)
echo.
pause
echo.
python auto_migrate_via_mcp.py
echo.
pause

