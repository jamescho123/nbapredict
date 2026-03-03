"""
Test Alternative Supabase Connection Methods
"""

import psycopg2
import socket

PASSWORD = 'Jcjc1749!!!!'

# All possible connection configurations
test_configs = [
    {
        'name': 'Direct - db prefix',
        'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
        'port': 5432,
        'user': 'postgres',
        'database': 'postgres'
    },
    {
        'name': 'Direct - no db prefix',
        'host': 'mxnpfsiyaqqwdcokukij.supabase.co',
        'port': 5432,
        'user': 'postgres',
        'database': 'postgres'
    },
    {
        'name': 'Pooler - Transaction mode',
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': 6543,
        'user': 'postgres.mxnpfsiyaqqwdcokukij',
        'database': 'postgres'
    },
    {
        'name': 'Pooler - Session mode',
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': 5432,
        'user': 'postgres.mxnpfsiyaqqwdcokukij',
        'database': 'postgres'
    },
    {
        'name': 'Pooler - Direct user',
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': 6543,
        'user': 'postgres',
        'database': 'postgres'
    },
    {
        'name': 'Regional Pooler - Transaction',
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': 6543,
        'user': 'postgres.mxnpfsiyaqqwdcokukij',
        'database': 'postgres'
    }
]

def test_connection(config):
    """Test a connection configuration"""
    print(f"\n{'='*70}")
    print(f"Testing: {config['name']}")
    print(f"Host: {config['host']}:{config['port']}")
    print(f"User: {config['user']}")
    print('='*70)
    
    # DNS check
    try:
        ip = socket.gethostbyname(config['host'])
        print(f"[OK] DNS resolved: {ip}")
    except Exception as e:
        print(f"[FAILED] DNS: {e}")
        return False
    
    # Connection test
    conn_config = {
        'host': config['host'],
        'port': config['port'],
        'database': config['database'],
        'user': config['user'],
        'password': PASSWORD,
        'connect_timeout': 15
    }
    
    try:
        print("Connecting...")
        conn = psycopg2.connect(**conn_config)
        cursor = conn.cursor()
        print("[SUCCESS] Connected!")
        
        # Test query
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"[OK] PostgreSQL version: {version[:50]}...")
        
        # Check NBA schema
        cursor.execute('''
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA'
        ''')
        table_count = cursor.fetchone()[0]
        print(f"[OK] NBA schema: {table_count} tables")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if 'timeout' in error_msg.lower():
            print(f"[FAILED] Connection timeout")
        elif 'authentication' in error_msg.lower():
            print(f"[FAILED] Authentication failed")
        elif 'tenant' in error_msg.lower() or 'user not found' in error_msg.lower():
            print(f"[FAILED] Tenant/user not found")
        else:
            print(f"[FAILED] {error_msg[:100]}")
        return False
    except Exception as e:
        print(f"[FAILED] {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUPABASE CONNECTION TEST - ALL METHODS")
    print("="*70)
    print(f"Project: mxnpfsiyaqqwdcokukij")
    print(f"Password: {'*' * len(PASSWORD)}")
    print("="*70)
    
    results = {}
    for config in test_configs:
        results[config['name']] = test_connection(config)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    success_count = sum(results.values())
    
    for name, success in results.items():
        status = "[SUCCESS]" if success else "[FAILED]"
        print(f"{status} {name}")
    
    print("="*70)
    
    if success_count > 0:
        print(f"\n[SUCCESS] {success_count} connection method(s) working!")
        print("\nWorking methods:")
        for name, success in results.items():
            if success:
                print(f"  - {name}")
    else:
        print("\n[FAILED] No connection methods working")
        print("\nTroubleshooting steps:")
        print("1. Check Supabase Dashboard:")
        print("   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/database")
        print("2. Verify connection string format")
        print("3. Check if project is active (not paused)")
        print("4. Try disconnecting from VPN")
        print("5. Check firewall settings for ports 5432, 6543")















