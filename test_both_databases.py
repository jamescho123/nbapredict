import asyncio
import json
from mcp_supabase_server import handle_call_tool, handle_read_resource

async def test_both_databases():
    print("=== Testing Both Local and Supabase Databases ===\n")
    
    print("1. Testing Local Database - Tables:")
    try:
        result = await handle_read_resource("local://tables")
        data = json.loads(result)
        print(f"   Source: {data.get('source')}")
        print(f"   Found {len(data.get('tables', []))} tables")
        print(f"   Tables: {', '.join(data.get('tables', [])[:5])}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Testing Supabase Database - Tables:")
    try:
        result = await handle_read_resource("supabase://tables")
        data = json.loads(result)
        print(f"   Source: {data.get('source')}")
        print(f"   Found {len(data.get('tables', []))} tables")
        print(f"   Tables: {', '.join(data.get('tables', [])[:5])}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Testing Local Database - Get Team Info:")
    try:
        result = await handle_call_tool(
            "get_team_info",
            {"team_name": "Lakers", "use_supabase": False}
        )
        data = json.loads(result[0].text)
        print(f"   Source: {data.get('source')}")
        print(f"   Found {len(data.get('teams', []))} team(s)")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing Supabase Database - Get Team Info:")
    try:
        result = await handle_call_tool(
            "get_team_info",
            {"team_name": "Lakers", "use_supabase": True}
        )
        data = json.loads(result[0].text)
        print(f"   Source: {data.get('source')}")
        print(f"   Found {len(data.get('teams', []))} team(s)")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Testing Compare Databases:")
    try:
        result = await handle_call_tool(
            "compare_databases",
            {"table_name": "Teams"}
        )
        data = json.loads(result[0].text)
        print(f"   Table: {data.get('table')}")
        print(f"   Local count: {data.get('local_count')}")
        print(f"   Supabase count: {data.get('supabase_count')}")
        print(f"   Difference: {data.get('difference')}")
        print(f"   In sync: {data.get('in_sync')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n6. Testing Compare Databases - Players:")
    try:
        result = await handle_call_tool(
            "compare_databases",
            {"table_name": "Players"}
        )
        data = json.loads(result[0].text)
        print(f"   Table: {data.get('table')}")
        print(f"   Local count: {data.get('local_count')}")
        print(f"   Supabase count: {data.get('supabase_count')}")
        print(f"   Difference: {data.get('difference')}")
        print(f"   In sync: {data.get('in_sync')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_both_databases())

