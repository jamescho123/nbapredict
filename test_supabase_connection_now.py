"""
Test Supabase Connection with Updated Credentials
"""

import psycopg2
import socket

SUPABASE_CONFIG = {
    'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'Jcjc1749!!!!',
    'port': 5432
}

SUPABASE_POOLER_CONFIG = {
    'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.mxnpfsiyaqqwdcokukij',
    'password': 'Jcjc1749!!!!',
    'port': 6543
}

DB_SCHEMA = 'NBA'

def test_dns(hostname):
    """Test DNS resolution"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"[OK] DNS: {hostname} -> {ip}")
        return True, ip
    except Exception as e:
        print(f"[FAILED] DNS: {hostname} - {e}")
        return False, None

def test_connection(config, name):
    """Test database connection"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"Host: {config['host']}:{config['port']}")
    print(f"User: {config['user']}")
    print('='*70)
    
    # DNS check
    dns_ok, ip = test_dns(config['host'])
    if not dns_ok:
        return False
    
    # Connection test
    try:
        print("Connecting...")
        conn = psycopg2.connect(**config, connect_timeout=15)
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
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if 'timeout' in error_msg.lower():
            print(f"[FAILED] Connection timeout - firewall likely blocking port {config['port']}")
        elif 'authentication' in error_msg.lower() or 'password' in error_msg.lower():
            print(f"[FAILED] Authentication failed - check password")
        elif 'tenant' in error_msg.lower() or 'user not found' in error_msg.lower():
            print(f"[FAILED] Tenant/user not found - project may not be ready")
        else:
            print(f"[FAILED] {error_msg}")
        return False
    except Exception as e:
        print(f"[FAILED] {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUPABASE CONNECTION TEST")
    print("="*70)
    print(f"Password: {'*' * len(SUPABASE_CONFIG['password'])}")
    print(f"Project: mxnpfsiyaqqwdcokukij")
    print("="*70)
    
    # Test direct connection
    direct_ok = test_connection(SUPABASE_CONFIG, "Direct Connection (Port 5432)")
    
    # Test pooler connection
    pooler_ok = test_connection(SUPABASE_POOLER_CONFIG, "Connection Pooler (Port 6543)")
    
    # Summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Direct Connection: {'[SUCCESS]' if direct_ok else '[FAILED]'}")
    print(f"Connection Pooler: {'[SUCCESS]' if pooler_ok else '[FAILED]'}")
    
    if direct_ok or pooler_ok:
        print("\n[SUCCESS] At least one connection method works!")
        if direct_ok:
            print("  -> Use direct connection for best performance")
        if pooler_ok:
            print("  -> Use connection pooler if direct fails")
    else:
        print("\n[FAILED] Neither connection method works")
        print("\nPossible issues:")
        print("1. Firewall blocking ports 5432 and 6543")
        print("2. VPN network restrictions")
        print("3. Project still initializing")
        print("4. Incorrect credentials")
        print("\nSolutions:")
        print("- Disconnect from VPN and try again")
        print("- Check Supabase dashboard for correct connection string")
        print("- Contact network admin to whitelist *.supabase.co")















