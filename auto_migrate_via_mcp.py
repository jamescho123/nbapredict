import asyncio
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

from mcp_supabase_server import handle_call_tool

async def test_connection():
    print("Testing Supabase connection...")
    try:
        result = await handle_call_tool("query_database", {
            "query": "SELECT 1",
            "use_supabase": True
        })
        print("✓ Supabase connection successful\n")
        return True
    except Exception as e:
        print(f"✗ Cannot connect to Supabase: {e}\n")
        print("Network connectivity issue detected.")
        print("Please use manual SQL upload method instead:")
        print("  See: UPLOAD_TO_SUPABASE.md")
        return False

async def migrate_single_table(table_name):
    print(f"Migrating table: {table_name}")
    try:
        result = await handle_call_tool("migrate_table", {
            "table_name": table_name,
            "truncate": True,
            "batch_size": 1000
        })
        
        data = json.loads(result[0].text)
        
        if data.get("status") == "success":
            print(f"  ✓ Migrated {data.get('rows_migrated')} rows")
            print(f"  Verified: {data.get('verified')}")
        elif data.get("status") == "skipped":
            print(f"  - Skipped (no data)")
        else:
            print(f"  ✗ Error: {data.get('error')}")
        
        return data
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"status": "error", "error": str(e)}

async def migrate_all_tables():
    print("="*60)
    print("NBA Database Automatic Migration via MCP")
    print("Local PostgreSQL → Supabase")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not await test_connection():
        return
    
    print("Starting full database migration...")
    print("="*60)
    
    try:
        result = await handle_call_tool("migrate_all_tables", {
            "batch_size": 1000
        })
        
        data = json.loads(result[0].text)
        
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        
        print(f"\nTables processed: {data.get('tables_processed')}")
        print(f"Total rows migrated: {data.get('total_rows_migrated')}")
        
        print("\nResults by table:")
        for table, result in data.get("results", {}).items():
            status = result.get("status")
            if status == "success":
                verified = "✓" if result.get("verified") else "⚠"
                print(f"  {verified} {table}: {result.get('rows_migrated')} rows")
            elif status == "skipped":
                print(f"  - {table}: skipped (no data)")
            elif status == "error":
                print(f"  ✗ {table}: {result.get('error')}")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'mcp_migration_report_{timestamp}.json'
        with open(report_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {report_file}")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print("\nIf you continue to have network issues,")
        print("please use the manual SQL upload method:")
        print("  See: UPLOAD_TO_SUPABASE.md")

async def main():
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        print(f"Migrating single table: {table_name}\n")
        
        if not await test_connection():
            return
        
        await migrate_single_table(table_name)
    else:
        await migrate_all_tables()

if __name__ == "__main__":
    asyncio.run(main())

