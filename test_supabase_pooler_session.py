"""
Test Supabase Session Pooler Connection (IPv4 Compatible)
"""

import psycopg2
from urllib.parse import quote_plus

PASSWORD = 'Jcjc1749!!!!'

# Session Pooler Configuration (IPv4 compatible)
SESSION_POOLER_CONFIG = {
    'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
    'port': 5432,  # Session mode uses port 5432
    'database': 'postgres',
    'user': 'postgres.mxnpfsiyaqqwdcokukij',  # Pooler requires project ID in username
    'password': PASSWORD
}

# Connection string format
CONNECTION_STRING = f"postgresql://{SESSION_POOLER_CONFIG['user']}:{quote_plus(PASSWORD)}@{SESSION_POOLER_CONFIG['host']}:{SESSION_POOLER_CONFIG['port']}/{SESSION_POOLER_CONFIG['database']}"

DB_SCHEMA = 'NBA'

def test_session_pooler():
    """Test Session Pooler connection"""
    print("\n" + "="*70)
    print("SUPABASE CONNECTION TEST - Session Pooler (IPv4 Compatible)")
    print("="*70)
    print(f"Host: {SESSION_POOLER_CONFIG['host']}:{SESSION_POOLER_CONFIG['port']}")
    print(f"User: {SESSION_POOLER_CONFIG['user']}")
    print(f"Database: {SESSION_POOLER_CONFIG['database']}")
    print("Mode: Session Pooler (IPv4 compatible)")
    print("="*70 + "\n")
    
    try:
        print("Connecting to Session Pooler...")
        conn = psycopg2.connect(**SESSION_POOLER_CONFIG, connect_timeout=30)
        cursor = conn.cursor()
        print("[SUCCESS] Connected to Supabase Session Pooler!")
        
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
        print("[SUCCESS] Supabase Session Pooler connection is working!")
        print("="*70)
        print("\nConnection Details:")
        print(f"  Host: {SESSION_POOLER_CONFIG['host']}")
        print(f"  Port: {SESSION_POOLER_CONFIG['port']} (Session mode)")
        print(f"  User: {SESSION_POOLER_CONFIG['user']}")
        print(f"  Database: {SESSION_POOLER_CONFIG['database']}")
        print("\nConnection String:")
        print(f"  postgresql://{SESSION_POOLER_CONFIG['user']}:***@{SESSION_POOLER_CONFIG['host']}:{SESSION_POOLER_CONFIG['port']}/{SESSION_POOLER_CONFIG['database']}")
        print("="*70)
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"\n[FAILED] Connection error: {error_msg}")
        
        if 'authentication' in error_msg.lower() or 'password' in error_msg.lower():
            print("\nPossible causes:")
            print("- Incorrect password")
            print("- Username format incorrect (should be postgres.mxnpfsiyaqqwdcokukij)")
        elif 'tenant' in error_msg.lower() or 'user not found' in error_msg.lower():
            print("\nPossible causes:")
            print("- Project ID incorrect in username")
            print("- Project not fully initialized")
            print("- Pooler not enabled for this project")
        elif 'timeout' in error_msg.lower():
            print("\nPossible causes:")
            print("- Firewall still blocking port 5432")
            print("- Network restrictions")
        else:
            print(f"\nError details: {error_msg}")
        
        return False
        
    except Exception as e:
        print(f"\n[FAILED] Unexpected error: {e}")
        return False

def test_connection_string():
    """Test using connection string format"""
    print("\n" + "="*70)
    print("TESTING CONNECTION STRING FORMAT")
    print("="*70)
    
    try:
        print("Connecting using connection string...")
        conn = psycopg2.connect(CONNECTION_STRING, connect_timeout=30)
        cursor = conn.cursor()
        print("[SUCCESS] Connection string method works!")
        
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"[OK] PostgreSQL: {version[:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[FAILED] Connection string: {e}")
        return False

if __name__ == "__main__":
    # Test Session Pooler
    pooler_ok = test_session_pooler()
    
    # Test connection string
    string_ok = test_connection_string()
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Session Pooler (Direct): {'[SUCCESS]' if pooler_ok else '[FAILED]'}")
    print(f"Session Pooler (String): {'[SUCCESS]' if string_ok else '[FAILED]'}")
    
    if pooler_ok or string_ok:
        print("\n[SUCCESS] Supabase is connected via Session Pooler!")
        print("\nNext steps:")
        print("1. Update db_config.py to use Session Pooler")
        print("2. Update mcp_supabase_server.py connection")
        print("3. Migrate data from local to Supabase")
        print("\nConnection String:")
        print(f"postgresql://postgres.mxnpfsiyaqqwdcokukij:{PASSWORD}@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres")
    else:
        print("\n[FAILED] Session Pooler connection not working")
        print("\nPlease check:")
        print("1. Project ID in username (postgres.mxnpfsiyaqqwdcokukij)")
        print("2. Password is correct")
        print("3. Session Pooler is enabled in Supabase dashboard")
        print("4. Network/firewall allows port 5432")















