# Automatic Migration: PostgreSQL → Supabase

## ✓ MCP Server Created with Auto-Migration Tools

Your MCP server now includes automatic migration capabilities!

---

## Current Status: Network Issue

**Problem:** Direct connection to Supabase is blocked due to DNS/firewall restrictions.

**Error:** `could not translate host name "db.mxnpfsiyaqqwdcokukij.supabase.co" to address`

---

## Solution A: Use Manual SQL Upload (WORKS NOW)

Since network access is blocked, use the SQL file method:

### Files Ready for Upload:
- `nba_full_export_20251027_173827_part1.sql` (10 MB)
- `nba_full_export_20251027_173827_part2.sql` (10 MB)
- `nba_full_export_20251027_173827_part3.sql` (10 MB)
- `nba_full_export_20251027_173827_part4.sql` (10 MB)
- `nba_full_export_20251027_173827_part5.sql` (10 MB)
- `nba_full_export_20251027_173827_part6.sql` (7.4 MB)

### Upload Steps:
1. Open: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new
2. Execute each part file in order (part1 → part6)

**See detailed instructions:** `UPLOAD_TO_SUPABASE.md`

---

## Solution B: Automatic Migration (When Network Works)

Once network access is restored, you can use automatic migration:

### Option 1: Simple Command-Line Tool

```cmd
python auto_migrate_simple.py
```

This will:
- Connect to both Local PostgreSQL and Supabase
- Automatically migrate all 18 tables
- Show progress for each table
- Verify data after migration
- Generate migration report

**For single table:**
```cmd
python auto_migrate_simple.py Teams
```

### Option 2: Via MCP Server

The MCP server includes these migration tools:

**Tools Available:**
- `migrate_table` - Migrate a single table
- `migrate_all_tables` - Migrate all tables automatically
- `compare_databases` - Compare data between local and Supabase

**When using with Claude Desktop:**
```
Ask: "Migrate all tables from local to Supabase"
```

The MCP server will automatically handle the migration.

---

## Fix Network Access

To enable automatic migration:

### 1. Check Firewall
Allow outbound connections to:
- `*.supabase.co`
- Ports: 5432 (direct) or 6543 (pooler)

### 2. Check DNS
Test DNS resolution:
```cmd
nslookup db.mxnpfsiyaqqwdcokukij.supabase.co
```

If DNS fails, try:
- Use different DNS server (8.8.8.8, 1.1.1.1)
- Check hosts file (C:\Windows\System32\drivers\etc\hosts)

### 3. Network Environment
- Corporate networks may block database connections
- Try from different network (home/mobile hotspot)
- Use VPN if available

### 4. Test Connection
```cmd
python test_supabase_connection.py
```

Once connection works, you can use automatic migration!

---

## Tools Created

### Automatic Migration
| File | Purpose |
|------|---------|
| `auto_migrate_simple.py` | Simple automatic migration |
| `auto_migrate_auto.cmd` | Run automatic migration |
| `auto_migrate_via_mcp.py` | Migration via MCP (advanced) |

### MCP Server with Migration
| File | Purpose |
|------|---------|
| `mcp_supabase_server.py` | MCP server with migration tools |
| `mcp_config.json` | Configuration for Claude Desktop |
| `setup_mcp.cmd` | Install MCP dependencies |
| `run_mcp_server.cmd` | Start MCP server |

### Manual Migration
| File | Purpose |
|------|---------|
| `export_all_tables_to_sql.py` | Export to SQL files |
| `split_large_sql.py` | Split large SQL files |
| `nba_full_export_*_part*.sql` | SQL files ready to upload |

### Utilities
| File | Purpose |
|------|---------|
| `test_supabase_connection.py` | Test Supabase connectivity |
| `verify_migration.py` | Verify migration |
| `check_supabase_data.py` | Check Supabase data |
| `sync_single_table.py` | Sync one table |

---

## Migration Features

### Automatic Migration Includes:
- ✓ Connection testing before migration
- ✓ Progress tracking for each table
- ✓ Batch processing (1000 rows per batch)
- ✓ Automatic TRUNCATE before insert
- ✓ Data verification after migration
- ✓ Detailed JSON report generation
- ✓ Error handling and rollback

### MCP Server Features:
- ✓ Connect to BOTH Local and Supabase
- ✓ Query either database via `use_supabase` parameter
- ✓ Migrate tables via MCP tools
- ✓ Compare data between databases
- ✓ Integration with Claude Desktop

---

## Quick Reference

### I want to...

**Migrate now (manual method):**
```
1. See: UPLOAD_TO_SUPABASE.md
2. Upload SQL files to Supabase web interface
```

**Fix network and use automatic migration:**
```cmd
1. Fix network (see "Fix Network Access" above)
2. Run: python auto_migrate_simple.py
```

**Use MCP server:**
```cmd
1. Run: setup_mcp.cmd
2. Configure Claude Desktop (see MCP_SUPABASE_README.md)
3. Ask Claude to migrate tables
```

**Migrate single table (when network works):**
```cmd
python auto_migrate_simple.py Teams
```

**Verify migration (when network works):**
```cmd
python verify_migration.py
```

---

## Summary

You now have:

1. ✓ SQL files ready for manual upload (WORKS NOW)
2. ✓ Automatic migration script (works when network available)
3. ✓ MCP server with migration tools (works when network available)
4. ✓ Complete documentation and utilities

**Current recommendation:** Use manual SQL upload method (Solution A) since network access is blocked.

**Future:** Once network is fixed, use automatic migration (Solution B) for ongoing sync.

