import asyncio
import json
from mcp_supabase_server import (
    handle_list_resources,
    handle_list_tools,
    handle_list_prompts,
    handle_call_tool,
    handle_read_resource,
)

async def test_mcp_server():
    print("=== Testing MCP Server ===\n")
    
    print("1. Testing Resources:")
    resources = await handle_list_resources()
    for resource in resources:
        print(f"  - {resource.name}: {resource.uri}")
    
    print("\n2. Testing Tools:")
    tools = await handle_list_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print("\n3. Testing Prompts:")
    prompts = await handle_list_prompts()
    for prompt in prompts:
        print(f"  - {prompt.name}: {prompt.description}")
    
    print("\n4. Testing Resource Read (Tables):")
    try:
        result = await handle_read_resource("supabase://tables")
        data = json.loads(result)
        print(f"  Found {len(data.get('tables', []))} tables")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n5. Testing Tool Call (Get Team Info):")
    try:
        result = await handle_call_tool(
            "get_team_info",
            {"team_name": "Lakers"}
        )
        print(f"  Result: {result[0].text[:200]}...")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n=== MCP Server Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())

