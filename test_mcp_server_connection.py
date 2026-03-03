"""
Test MCP Server Connection and Functionality
"""

import subprocess
import sys
import os

def check_mcp_module():
    """Check if MCP module is installed"""
    print("\n" + "="*70)
    print("MCP MODULE CHECK")
    print("="*70)
    
    try:
        import mcp
        print("[OK] MCP module is installed")
        if hasattr(mcp, '__version__'):
            print(f"     Version: {mcp.__version__}")
        return True
    except ImportError:
        print("[FAILED] MCP module NOT installed")
        print("\nTo install:")
        print("  pip install -r requirements_mcp.txt")
        return False

def check_mcp_server_file():
    """Check if MCP server file exists"""
    print("\n" + "="*70)
    print("MCP SERVER FILE CHECK")
    print("="*70)
    
    server_file = "mcp_supabase_server.py"
    if os.path.exists(server_file):
        print(f"[OK] MCP server file exists: {server_file}")
        return True
    else:
        print(f"[FAILED] MCP server file not found: {server_file}")
        return False

def check_mcp_config():
    """Check MCP configuration"""
    print("\n" + "="*70)
    print("MCP CONFIGURATION CHECK")
    print("="*70)
    
    config_file = "mcp_config.json"
    if os.path.exists(config_file):
        print(f"[OK] MCP config file exists: {config_file}")
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"     Server name: {list(config.get('mcpServers', {}).keys())[0] if config.get('mcpServers') else 'None'}")
            return True
        except Exception as e:
            print(f"[FAILED] Error reading config: {e}")
            return False
    else:
        print(f"[FAILED] MCP config file not found: {config_file}")
        return False

def test_mcp_server_import():
    """Test if MCP server can be imported"""
    print("\n" + "="*70)
    print("MCP SERVER IMPORT TEST")
    print("="*70)
    
    try:
        # Try importing the server module
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from mcp_supabase_server import get_db_connection
        
        print("[OK] MCP server module can be imported")
        
        # Test database connection functions
        print("\nTesting database connection functions...")
        
        # Test local connection
        try:
            conn = get_db_connection(use_supabase=False)
            cursor = conn.cursor()
            cursor.execute('SELECT version()')
            version = cursor.fetchone()[0]
            print(f"[OK] Local PostgreSQL connection works")
            print(f"     Version: {version[:50]}...")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[FAILED] Local connection: {e}")
        
        # Test Supabase connection
        try:
            conn = get_db_connection(use_supabase=True)
            cursor = conn.cursor()
            cursor.execute('SELECT version()')
            version = cursor.fetchone()[0]
            print(f"[OK] Supabase connection works")
            print(f"     Version: {version[:50]}...")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[FAILED] Supabase connection: {e}")
            print("     (This is expected if Supabase is not connected)")
        
        return True
        
    except ImportError as e:
        print(f"[FAILED] Cannot import MCP server: {e}")
        print("     This is expected if MCP module is not installed")
        return False
    except Exception as e:
        print(f"[FAILED] Error: {e}")
        return False

def check_claude_desktop_config():
    """Check if Claude Desktop is configured"""
    print("\n" + "="*70)
    print("CLAUDE DESKTOP CONFIGURATION")
    print("="*70)
    
    import os
    config_path = os.path.join(os.getenv('APPDATA', ''), 'Claude', 'claude_desktop_config.json')
    
    if os.path.exists(config_path):
        print(f"[OK] Claude Desktop config found: {config_path}")
        try:
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
            servers = config.get('mcpServers', {})
            if servers:
                print(f"     Configured servers: {', '.join(servers.keys())}")
                return True
            else:
                print("     No MCP servers configured")
                return False
        except Exception as e:
            print(f"[FAILED] Error reading config: {e}")
            return False
    else:
        print(f"[INFO] Claude Desktop config not found")
        print(f"     Expected location: {config_path}")
        print("     MCP only works in Claude Desktop, not in Cursor")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MCP SERVER CONNECTION TEST")
    print("="*70)
    print("\nNote: MCP (Model Context Protocol) is designed for Claude Desktop.")
    print("I (Claude in Cursor) do NOT have direct MCP tool access.")
    print("This test checks if the MCP server is properly configured.")
    print("="*70)
    
    results = {
        'mcp_module': check_mcp_module(),
        'server_file': check_mcp_server_file(),
        'mcp_config': check_mcp_config(),
        'server_import': test_mcp_server_import(),
        'claude_desktop': check_claude_desktop_config()
    }
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for check, result in results.items():
        status = "[OK]" if result else "[FAILED]"
        print(f"{status} {check.replace('_', ' ').title()}")
    
    print("="*70)
    
    if all(results.values()):
        print("\n[SUCCESS] MCP server is properly configured!")
        print("\nTo use MCP:")
        print("1. Install Claude Desktop app")
        print("2. Configure mcp_config.json in Claude Desktop")
        print("3. Restart Claude Desktop")
        print("4. MCP tools will be available in Claude Desktop")
    else:
        print("\n[INFO] MCP server needs configuration")
        print("\nCurrent status:")
        if not results['mcp_module']:
            print("- Install MCP module: pip install -r requirements_mcp.txt")
        if not results['claude_desktop']:
            print("- MCP only works in Claude Desktop (not Cursor)")
            print("- Install Claude Desktop to use MCP features")
    
    print("\n" + "="*70)
    print("IMPORTANT: MCP ACCESS")
    print("="*70)
    print("\nI (Claude in Cursor) CANNOT directly access MCP tools.")
    print("MCP is only available in Claude Desktop application.")
    print("\nHowever, I CAN:")
    print("1. Help configure the MCP server")
    print("2. Test database connections directly")
    print("3. Update configuration files")
    print("4. Help with MCP server code")
    print("\nTo use MCP features, you need Claude Desktop app.")
    print("="*70 + "\n")















