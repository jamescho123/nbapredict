# Supabase MCP Setup in Cursor

## What is Supabase MCP?

Supabase MCP (Model Context Protocol) allows Cursor's AI to directly interact with your Supabase database:
- Query tables
- Read schemas
- Execute SQL
- Manage data
- All through natural language in Cursor!

## Prerequisites

- ✓ Node.js installed (v18 or higher)
- ✓ Supabase project (you have: mxnpfsiyaqqwdcokukij)
- ✓ Cursor IDE

## Step 1: Install Supabase MCP Server

Open terminal in Cursor (Ctrl+`):

```bash
npm install -g @modelcontextprotocol/server-supabase
```

Or using npx (no installation needed):
```bash
npx @modelcontextprotocol/server-supabase
```

## Step 2: Get Supabase Credentials

You need these from your Supabase project:

1. **Project URL:**
   ```
   https://mxnpfsiyaqqwdcokukij.supabase.co
   ```

2. **Service Role Key:**
   - Go to: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/api
   - Copy the `service_role` key (secret, not anon key!)
   - Keep this safe - it has admin access!

3. **Database Password:**
   ```
   VXUXqY9Uofg9ujoo
   ```

## Step 3: Configure Cursor MCP

### Option A: Using Cursor Settings UI

1. Open Cursor Settings (Ctrl+,)
2. Search for "MCP" or "Model Context Protocol"
3. Click "Edit MCP Settings"
4. Add Supabase MCP configuration

### Option B: Edit Config File Directly

1. Open Cursor config file:
   - Windows: `%APPDATA%\Cursor\User\globalStorage\settings.json`
   - Or press Ctrl+Shift+P → "Preferences: Open User Settings (JSON)"

2. Add this configuration:

```json
{
  "mcp": {
    "servers": {
      "supabase": {
        "command": "npx",
        "args": [
          "@modelcontextprotocol/server-supabase"
        ],
        "env": {
          "SUPABASE_URL": "https://mxnpfsiyaqqwdcokukij.supabase.co",
          "SUPABASE_SERVICE_ROLE_KEY": "YOUR_SERVICE_ROLE_KEY_HERE",
          "SUPABASE_DB_PASSWORD": "VXUXqY9Uofg9ujoo"
        }
      }
    }
  }
}
```

3. Replace `YOUR_SERVICE_ROLE_KEY_HERE` with your actual service role key

## Step 4: Alternative - Use .env File

Create a `.env` file in your project root:

```env
# Supabase MCP Configuration
SUPABASE_URL=https://mxnpfsiyaqqwdcokukij.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_DB_PASSWORD=VXUXqY9Uofg9ujoo
```

Then in Cursor settings:

```json
{
  "mcp": {
    "servers": {
      "supabase": {
        "command": "npx",
        "args": [
          "@modelcontextprotocol/server-supabase"
        ],
        "env": {
          "SUPABASE_URL": "${env:SUPABASE_URL}",
          "SUPABASE_SERVICE_ROLE_KEY": "${env:SUPABASE_SERVICE_ROLE_KEY}",
          "SUPABASE_DB_PASSWORD": "${env:SUPABASE_DB_PASSWORD}"
        }
      }
    }
  }
}
```

## Step 5: Restart Cursor

Close and reopen Cursor to load the MCP configuration.

## Step 6: Test the Connection

In Cursor chat, try:

```
@supabase List all tables in the NBA schema
```

or

```
@supabase Show me the structure of the Matches table
```

or

```
@supabase How many rows are in the VectorNews table?
```

## Example MCP Configuration File

Complete example for `cursor_mcp_config.json`:

```json
{
  "mcpServers": {
    "supabase-nba": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-supabase"
      ],
      "env": {
        "SUPABASE_URL": "https://mxnpfsiyaqqwdcokukij.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "SUPABASE_DB_PASSWORD": "VXUXqY9Uofg9ujoo"
      }
    }
  }
}
```

## What You Can Do With Supabase MCP

Once configured, you can ask Cursor to:

### Database Queries:
- "Show me all NBA teams"
- "Find matches from 2024-25 season"
- "Get player statistics"
- "Query news with vector embeddings"

### Schema Operations:
- "What's the structure of the Players table?"
- "List all tables in NBA schema"
- "Show relationships between tables"

### Data Management:
- "Insert a new player"
- "Update team information"
- "Delete old records"

### Analysis:
- "Analyze match trends"
- "Find correlations in the data"
- "Generate reports from the database"

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit service_role key to git**
   - Add `.env` to `.gitignore`
   - Use environment variables

2. **Service role key has full admin access**
   - Can read/write/delete all data
   - Keep it secret!

3. **Alternative: Use anon key with RLS**
   - More secure but limited access
   - Enable Row Level Security in Supabase

## Troubleshooting

### "MCP server not found"
```bash
# Install globally
npm install -g @modelcontextprotocol/server-supabase

# Or check Node.js version
node --version  # Should be v18+
```

### "Connection refused"
- Check Supabase project is active
- Verify credentials are correct
- Test connection: `python test_connection_now.py`

### "Permission denied"
- Verify you're using `service_role` key, not `anon` key
- Check database password is correct

### MCP not showing in Cursor
- Restart Cursor completely
- Check config file syntax (valid JSON)
- Look for errors in Cursor developer console (Ctrl+Shift+I)

## Alternative: Direct SQL in Cursor

If MCP doesn't work, you can still query Supabase from Cursor:

Create `query_supabase.py`:

```python
import psycopg2

# Your Supabase connection
conn = psycopg2.connect(
    host='db.mxnpfsiyaqqwdcokukij.supabase.co',
    database='postgres',
    user='postgres',
    password='VXUXqY9Uofg9ujoo',
    port=5432
)

# Query example
cursor = conn.cursor()
cursor.execute('SELECT * FROM "NBA"."Teams" LIMIT 10;')
for row in cursor.fetchall():
    print(row)

conn.close()
```

Then ask Cursor: "Run query_supabase.py and show me the results"

## Resources

- Supabase MCP Docs: https://github.com/modelcontextprotocol/servers/tree/main/src/supabase
- MCP Protocol: https://modelcontextprotocol.io
- Your Supabase Dashboard: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij

## Summary

1. Install: `npm install -g @modelcontextprotocol/server-supabase`
2. Get service_role key from Supabase dashboard
3. Configure in Cursor settings
4. Restart Cursor
5. Test with `@supabase` commands

Your database will then be directly accessible through Cursor's AI!

