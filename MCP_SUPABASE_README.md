# Model Context Protocol (MCP) Server for NBA Databases

Connects to both Local PostgreSQL and Supabase simultaneously.

## Installation

```cmd
setup_mcp.cmd
```

Or manually:
```cmd
pip install -r requirements_mcp.txt
```

## Usage

### With Claude Desktop

1. Install dependencies: `setup_mcp.cmd`
2. Add to Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "nba-database": {
      "command": "python",
      "args": [
        "C:\\Users\\hp\\OneDrive\\文档\\GitHub\\nbapredict\\mcp_supabase_server.py"
      ]
    }
  }
}
```

3. Restart Claude Desktop

### Standalone Testing

```cmd
python test_mcp_server.py
```

## Available Resources

### Local Database
- `local://tables` - List all local database tables
- `local://teams` - NBA teams from local PostgreSQL
- `local://players` - NBA players from local PostgreSQL
- `local://matches` - NBA matches from local PostgreSQL
- `local://news` - NBA news from local PostgreSQL

### Supabase Database
- `supabase://tables` - List all Supabase database tables
- `supabase://teams` - NBA teams from Supabase
- `supabase://players` - NBA players from Supabase
- `supabase://matches` - NBA matches from Supabase
- `supabase://news` - NBA news from Supabase

## Available Tools

All tools accept `use_supabase` parameter (default: false)

- `query_database` - Execute SQL queries on local or Supabase
- `get_team_info` - Get team information from local or Supabase
- `get_player_stats` - Get player statistics from local or Supabase
- `predict_game` - Predict game outcomes (not implemented)
- `search_news` - Search NBA news from local or Supabase
- `compare_databases` - Compare data between local and Supabase

## Available Prompts

- `analyze_team_performance` - Analyze team performance
- `compare_players` - Compare two players
- `recent_news_summary` - Summarize recent news

## Database Connections

### Local PostgreSQL
- Host: localhost
- Database: James
- Schema: NBA
- User: postgres

### Supabase
- Host: db.mxnpfsiyaqqwdcokukij.supabase.co
- Database: postgres
- Schema: NBA
- User: postgres
- Port: 5432

