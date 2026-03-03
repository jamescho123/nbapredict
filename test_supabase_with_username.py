"""
Test Supabase Connection with Correct Username
Tests both Session Pooler and Direct Connection
"""

import psycopg2
from urllib.parse import quote_plus

PASSWORD = 'Jcjc1749!!!!'
USERNAME = 'jamescho@jumbosoft.com'
PROJECT_ID = 'mxnpfsiyaqqwdcokukij'

# Session Pooler Configuration
SESSION_POOLER_CONFIG = {
    'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
    'port': 5432,
    'database': 'postgres',
    'user': USERNAME,
    'password': PASSWORD
}

# Direct Connection Configuration
DIRECT_CONFIG = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'port': 5432,
    'database': 'postgres',
    'user': USERNAME,
    'password': PASSWORD
}

DB_SCHEMA = 'NBA'

def test_connection(config, name):
    """Test a connection configuration"""
    print("\n" + "="*70)
    print(f"TESTING: {name}")
    print("="*70)
    print(f"Host: {config['host']}:{config['port']}")
    print(f"User: {config['user']}")
    print(f"Database: {config['database']}")
    print("="*70 + "\n")
    
    try:
        print("Connecting...")
        conn = psycopg2.connect(**config, connect_timeout=30)
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
            LIMIT 10
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"[OK] Sample tables: {', '.join(tables)}")
        
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
        print(f"[SUCCESS] {name} connection is working!")
        print("="*70)
        
        # Generate connection string
        conn_string = f"postgresql://{config['user']}:{quote_plus(config['password'])}@{config['host']}:{config['port']}/{config['database']}"
        print(f"\nConnection String:")
        print(f"postgresql://{config['user']}:***@{config['host']}:{config['port']}/{config['database']}")
        print("="*70)
        
        return True, conn_string
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"\n[FAILED] Connection error: {error_msg[:200]}")
        
        if 'timeout' in error_msg.lower():
            print("\nPossible causes:")
            print("- Firewall blocking port")
            print("- Network restrictions")
        elif 'authentication' in error_msg.lower() or 'password' in error_msg.lower():
            print("\nPossible causes:")
            print("- Incorrect password")
            print("- Username incorrect")
        elif 'tenant' in error_msg.lower() or 'user not found' in error_msg.lower():
            print("\nPossible causes:")
            print("- User doesn't exist")
            print("- Pooler not enabled")
        else:
            print(f"\nError: {error_msg[:100]}")
        
        return False, None
        
    except Exception as e:
        print(f"\n[FAILED] Unexpected error: {e}")
        return False, None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUPABASE CONNECTION TEST")
    print("="*70)
    print(f"Username: {USERNAME}")
    print(f"Project ID: {PROJECT_ID}")
    print("="*70)
    
    # Test Session Pooler first
    print("\n>>> STEP 1: Testing Session Pooler (IPv4 compatible)")
    pooler_ok, pooler_string = test_connection(SESSION_POOLER_CONFIG, "Session Pooler")
    
    # Test Direct Connection if pooler fails
    if not pooler_ok:
        print("\n>>> STEP 2: Testing Direct Connection (original method)")
        direct_ok, direct_string = test_connection(DIRECT_CONFIG, "Direct Connection")
    else:
        direct_ok = False
        direct_string = None
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Session Pooler: {'[SUCCESS]' if pooler_ok else '[FAILED]'}")
    print(f"Direct Connection: {'[SUCCESS]' if direct_ok else '[FAILED]'}")
    print("="*70)
    
    if pooler_ok:
        print("\n[SUCCESS] Session Pooler is working!")
        print("\nRecommended Configuration:")
        print(f"  Host: {SESSION_POOLER_CONFIG['host']}")
        print(f"  Port: {SESSION_POOLER_CONFIG['port']}")
        print(f"  User: {SESSION_POOLER_CONFIG['user']}")
        print(f"  Database: {SESSION_POOLER_CONFIG['database']}")
        print(f"\nConnection String:")
        print(f"  {pooler_string}")
        
    elif direct_ok:
        print("\n[SUCCESS] Direct Connection is working!")
        print("\nRecommended Configuration:")
        print(f"  Host: {DIRECT_CONFIG['host']}")
        print(f"  Port: {DIRECT_CONFIG['port']}")
        print(f"  User: {DIRECT_CONFIG['user']}")
        print(f"  Database: {DIRECT_CONFIG['database']}")
        print(f"\nConnection String:")
        print(f"  {direct_string}")
        
    else:
        print("\n[FAILED] Neither connection method worked")
        print("\nPlease verify:")
        print("1. Username is correct: jamescho@jumbosoft.com")
        print("2. Password is correct")
        print("3. User has database access permissions")
        print("4. Project is active in Supabase dashboard")















