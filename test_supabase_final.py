"""
Final Supabase Connection Test - All Methods
"""

import psycopg2
from urllib.parse import quote_plus

PASSWORD = 'Jcjc1749!!!!'
USERNAME = 'jamescho@jumbosoft.com'
PROJECT_ID = 'mxnpfsiyaqqwdcokukij'

DB_SCHEMA = 'NBA'

# All connection methods to try
CONNECTION_METHODS = [
    {
        'name': 'Session Pooler - Standard User',
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': 5432,
        'user': USERNAME,
        'database': 'postgres'
    },
    {
        'name': 'Session Pooler - With Project ID',
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': 5432,
        'user': f'postgres.{PROJECT_ID}',
        'database': 'postgres'
    },
    {
        'name': 'Direct Connection - Standard User',
        'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
        'port': 5432,
        'user': USERNAME,
        'database': 'postgres'
    },
    {
        'name': 'Direct Connection - Postgres User',
        'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
        'port': 5432,
        'user': 'postgres',
        'database': 'postgres'
    }
]

def test_method(config):
    """Test a connection method"""
    print(f"\n{'='*70}")
    print(f"Testing: {config['name']}")
    print(f"Host: {config['host']}:{config['port']}")
    print(f"User: {config['user']}")
    print('='*70)
    
    try:
        print("Connecting...")
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=PASSWORD,
            connect_timeout=30
        )
        cursor = conn.cursor()
        print("[SUCCESS] Connected!")
        
        # Test query
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"[OK] PostgreSQL: {version[:50]}...")
        
        # Check NBA schema
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = '{DB_SCHEMA}'
        """)
        table_count = cursor.fetchone()[0]
        print(f"[OK] NBA schema: {table_count} tables")
        
        cursor.close()
        conn.close()
        
        # Generate connection string
        conn_string = f"postgresql://{config['user']}:{quote_plus(PASSWORD)}@{config['host']}:{config['port']}/{config['database']}"
        
        print(f"\n[SUCCESS] {config['name']} works!")
        print(f"Connection String:")
        print(f"postgresql://{config['user']}:***@{config['host']}:{config['port']}/{config['database']}")
        
        return True, config, conn_string
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if 'timeout' in error_msg.lower():
            print(f"[FAILED] Connection timeout (IPv6/firewall issue)")
        elif 'tenant' in error_msg.lower() or 'user not found' in error_msg.lower():
            print(f"[FAILED] Tenant/user not found")
        elif 'authentication' in error_msg.lower():
            print(f"[FAILED] Authentication failed")
        else:
            print(f"[FAILED] {error_msg[:80]}")
        return False, None, None
    except Exception as e:
        print(f"[FAILED] {e}")
        return False, None, None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUPABASE CONNECTION TEST - ALL METHODS")
    print("="*70)
    print(f"Username: {USERNAME}")
    print(f"Project ID: {PROJECT_ID}")
    print("="*70)
    
    working_config = None
    working_string = None
    
    for method in CONNECTION_METHODS:
        success, config, conn_string = test_method(method)
        if success:
            working_config = config
            working_string = conn_string
            break
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    if working_config:
        print(f"[SUCCESS] Working method: {working_config['name']}")
        print("\nConfiguration to use:")
        print(f"  Host: {working_config['host']}")
        print(f"  Port: {working_config['port']}")
        print(f"  User: {working_config['user']}")
        print(f"  Database: {working_config['database']}")
        print(f"  Password: {PASSWORD}")
        print(f"\nConnection String:")
        print(f"  {working_string}")
        print("\nNext steps:")
        print("1. Update db_config.py with these settings")
        print("2. Update mcp_supabase_server.py")
        print("3. Test data migration")
    else:
        print("[FAILED] No connection method worked")
        print("\nIssues found:")
        print("1. Session Pooler: Tenant/user not found (pooler may not be enabled)")
        print("2. Direct Connection: Timeout (IPv6/firewall blocking)")
        print("\nSolutions:")
        print("1. Enable Session Pooler in Supabase Dashboard:")
        print("   Settings > Database > Connection Pooling > Enable")
        print("2. Or use Supabase Web Dashboard for now:")
        print("   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/editor")
        print("3. Or configure firewall to allow port 5432")















