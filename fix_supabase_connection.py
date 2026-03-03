"""
Fix Supabase Connection - Force IPv4 and Test
"""

import psycopg2
import socket
import sys

PASSWORD = 'Jcjc1749!!!!'
HOST = 'db.mxnpfsiyaqqwdcokukij.supabase.co'
PORT = 5432
USER = 'postgres'
DATABASE = 'postgres'

def force_ipv4_connection():
    """Force IPv4 connection by resolving and using IP directly"""
    print("\n" + "="*70)
    print("SUPABASE CONNECTION - IPv4 FORCED")
    print("="*70)
    
    # Resolve to IPv4
    print(f"Resolving IPv4 for {HOST}...")
    try:
        # Force IPv4 only
        addr_info = socket.getaddrinfo(HOST, PORT, socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        if addr_info:
            ipv4 = addr_info[0][4][0]
            print(f"[OK] IPv4 address: {ipv4}")
        else:
            print("[FAILED] No IPv4 address found")
            return False
    except Exception as e:
        print(f"[FAILED] DNS resolution: {e}")
        print("\nTrying with hostname directly...")
        ipv4 = HOST
    
    print(f"\nConnecting to {ipv4}:{PORT}...")
    print(f"User: {USER}")
    print(f"Database: {DATABASE}")
    print("="*70 + "\n")
    
    try:
        # Try connection with longer timeout
        print("Attempting connection (30 second timeout)...")
        conn = psycopg2.connect(
            host=ipv4,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            connect_timeout=30
        )
        cursor = conn.cursor()
        print("[SUCCESS] Connected to Supabase!")
        
        # Test queries
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"[OK] PostgreSQL: {version[:50]}...")
        
        cursor.execute('''
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA'
        ''')
        table_count = cursor.fetchone()[0]
        print(f"[OK] NBA schema: {table_count} tables")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("[SUCCESS] Supabase connection is working!")
        print("="*70)
        print("\nYou can now:")
        print("1. Update db_config.py to use Supabase")
        print("2. Migrate data from local to Supabase")
        print("3. Use Supabase in MCP server")
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"\n[FAILED] Connection error: {error_msg}")
        
        if 'timeout' in error_msg.lower():
            print("\n" + "="*70)
            print("CONNECTION TIMEOUT - FIREWALL/NETWORK BLOCK")
            print("="*70)
            print("\nPort 5432 is being blocked. Solutions:")
            print("\n1. WINDOWS FIREWALL:")
            print("   - Open Windows Security")
            print("   - Go to Firewall & network protection")
            print("   - Click 'Allow an app through firewall'")
            print("   - Add Python or allow port 5432 (outbound)")
            print("\n2. ANTIVIRUS:")
            print("   - Temporarily disable to test")
            print("   - Add exception for Python")
            print("\n3. NETWORK:")
            print("   - Try mobile hotspot")
            print("   - Check if on corporate network")
            print("   - Contact network admin")
            print("\n4. SUPABASE DASHBOARD:")
            print("   - Verify project is active")
            print("   - Check connection settings")
            print("   - Try connection pooler instead")
        
        return False
        
    except Exception as e:
        print(f"\n[FAILED] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = force_ipv4_connection()
    
    if not success:
        print("\n" + "="*70)
        print("ALTERNATIVE: Use Supabase Web Dashboard")
        print("="*70)
        print("\nWhile fixing network issues, you can:")
        print("1. Access Supabase SQL Editor:")
        print("   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new")
        print("\n2. Use Supabase API instead of direct PostgreSQL")
        print("\n3. Set up SSH tunnel (if you have a server)")
        print("="*70 + "\n")
        
        sys.exit(1)
    else:
        sys.exit(0)















