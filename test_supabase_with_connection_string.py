"""
Test Supabase Connection Using Connection String Format
"""

import psycopg2
from urllib.parse import quote_plus

# Connection details
PASSWORD = 'Jcjc1749!!!!'
HOST = 'db.mxnpfsiyaqqwdcokukij.supabase.co'
PORT = 5432
USER = 'postgres'
DATABASE = 'postgres'

# Connection string format provided by user
CONNECTION_STRING = f'postgresql://{USER}:{quote_plus(PASSWORD)}@{HOST}:{PORT}/{DATABASE}'

DB_SCHEMA = 'NBA'

def test_connection_string():
    """Test using connection string"""
    print("\n" + "="*70)
    print("SUPABASE CONNECTION TEST - Connection String Method")
    print("="*70)
    print(f"Connection String: postgresql://{USER}:***@{HOST}:{PORT}/{DATABASE}")
    print("="*70 + "\n")
    
    try:
        print("Connecting using connection string...")
        conn = psycopg2.connect(CONNECTION_STRING, connect_timeout=15)
        cursor = conn.cursor()
        print("[SUCCESS] Connected!")
        
        # Test query
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"[OK] PostgreSQL: {version[:60]}...")
        
        # Check NBA schema
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = '{DB_SCHEMA}'
        """)
        table_count = cursor.fetchone()[0]
        print(f"[OK] NBA schema: {table_count} tables found")
        
        # List tables
        cursor.execute(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{DB_SCHEMA}'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"[OK] Tables: {', '.join(tables[:10])}")
        if len(tables) > 10:
            print(f"     ... and {len(tables) - 10} more")
        
        # Test a simple query
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM "{DB_SCHEMA}"."Teams"
        """)
        team_count = cursor.fetchone()[0]
        print(f"[OK] Teams table: {team_count} teams")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("[SUCCESS] Supabase connection is working!")
        print("="*70)
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"\n[FAILED] Connection error: {error_msg}")
        
        if 'timeout' in error_msg.lower():
            print("\nPossible causes:")
            print("- Firewall still blocking port 5432")
            print("- Network restrictions")
            print("- Supabase project not fully initialized")
        elif 'authentication' in error_msg.lower() or 'password' in error_msg.lower():
            print("\nPossible causes:")
            print("- Incorrect password")
            print("- User account issue")
        elif 'could not translate host name' in error_msg.lower():
            print("\nPossible causes:")
            print("- DNS resolution issue")
            print("- Hostname incorrect")
        else:
            print(f"\nError details: {error_msg}")
        
        return False
        
    except Exception as e:
        print(f"\n[FAILED] Unexpected error: {e}")
        return False

def test_direct_params():
    """Test using direct parameters (alternative method)"""
    print("\n" + "="*70)
    print("SUPABASE CONNECTION TEST - Direct Parameters Method")
    print("="*70)
    print(f"Host: {HOST}:{PORT}")
    print(f"User: {USER}")
    print(f"Database: {DATABASE}")
    print("="*70 + "\n")
    
    try:
        print("Connecting using direct parameters...")
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            connect_timeout=15
        )
        cursor = conn.cursor()
        print("[SUCCESS] Connected!")
        
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"[OK] PostgreSQL: {version[:60]}...")
        
        cursor.close()
        conn.close()
        
        print("\n[SUCCESS] Direct parameters method also works!")
        return True
        
    except Exception as e:
        print(f"\n[FAILED] Direct parameters: {e}")
        return False

if __name__ == "__main__":
    # Test connection string method
    string_ok = test_connection_string()
    
    # Test direct parameters method
    direct_ok = test_direct_params()
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Connection String Method: {'[SUCCESS]' if string_ok else '[FAILED]'}")
    print(f"Direct Parameters Method: {'[SUCCESS]' if direct_ok else '[FAILED]'}")
    
    if string_ok or direct_ok:
        print("\n[SUCCESS] Supabase is connected!")
        print("\nYou can now:")
        print("1. Use Supabase in your MCP server")
        print("2. Migrate data from local to Supabase")
        print("3. Use Supabase for predictions")
    else:
        print("\n[FAILED] Connection still not working")
        print("\nPlease check:")
        print("1. Supabase dashboard - project status")
        print("2. Connection string format")
        print("3. Password is correct")
        print("4. Network/firewall settings")















