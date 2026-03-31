@echo off
echo Installing MCP requirements...
pip install -r requirements_mcp.txt
echo.
echo MCP Server installed!
echo.
echo To use with Claude Desktop, add this to your Claude Desktop config:
echo %APPDATA%\Claude\claude_desktop_config.json
echo.
echo Add the contents of mcp_config.json to your Claude Desktop config.
pause

