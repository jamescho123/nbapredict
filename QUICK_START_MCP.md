# Quick Start: Supabase MCP in Cursor

## 1. Install (30 seconds)

Run this:
```bash
setup_supabase_mcp.cmd
```

Or manually:
```bash
npm install -g @modelcontextprotocol/server-supabase
```

## 2. Get Service Role Key (1 minute)

1. Go to: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/api
2. Scroll to "Project API keys"
3. Copy the `service_role` key (secret - looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

⚠️ **Not the `anon` key!** You need the `service_role` key.

## 3. Configure Cursor (2 minutes)

### Windows:

1. Press `Ctrl + Shift + P`
2. Type: "Preferences: Open User Settings (JSON)"
3. Add this to your settings:

```json
{
  "mcp": {
    "servers": {
      "supabase": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-supabase"],
        "env": {
          "SUPABASE_URL": "https://mxnpfsiyaqqwdcokukij.supabase.co",
          "SUPABASE_SERVICE_ROLE_KEY": "PASTE_YOUR_KEY_HERE",
          "SUPABASE_DB_PASSWORD": "VXUXqY9Uofg9ujoo"
        }
      }
    }
  }
}
```

4. Replace `PASTE_YOUR_KEY_HERE` with your actual service role key

## 4. Restart Cursor

Close Cursor completely and reopen it.

## 5. Test It! (10 seconds)

In Cursor chat, type:

```
@supabase List all tables in the NBA schema
```

You should see your tables listed!

## Example Commands

Once working, try:

```
@supabase Show me the structure of the Matches table
```

```
@supabase How many teams are in the Teams table?
```

```
@supabase Get the latest 5 news from Season2024_25_News
```

```
@supabase Query players from the Sacramento Kings
```

## Troubleshooting

### "MCP server not found"
- Make sure Node.js is installed: `node --version`
- Reinstall: `npm install -g @modelcontextprotocol/server-supabase`

### "Connection failed"
- Check service_role key is correct
- Verify Supabase project is active
- Test manual connection: `python test_connection_now.py`

### Not showing in Cursor
- Restart Cursor completely
- Check JSON syntax in settings (no trailing commas!)
- Open Developer Tools (Ctrl+Shift+I) and check for errors

## Complete Setup File

See `SUPABASE_MCP_SETUP.md` for detailed instructions and troubleshooting.

## What's Next?

Once MCP is working, you can:
- Query your NBA data directly from Cursor
- Ask Cursor to analyze game statistics
- Have Cursor write SQL queries for you
- Get insights from your vector embeddings

Your NBA prediction database is now fully accessible through Cursor's AI! 🎉

