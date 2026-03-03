"""
Test Supabase Connection - Force IPv4
"""

import psycopg2
import socket
from urllib.parse import quote_plus

PASSWORD = 'Jcjc1749!!!!'
HOST = 'db.mxnpfsiyaqqwdcokukij.supabase.co'
PORT = 5432
USER = 'postgres'
DATABASE = 'postgres'

def get_ipv4_address(hostname):
    """Get IPv4 address for hostname"""
    try:
        # Get all addresses
        addr_info = socket.getaddrinfo(hostname, PORT, socket.AF_INET, socket.SOCK_STREAM)
        ipv4_addresses = [info[4][0] for info in addr_info if info[0] == socket.AF_INET]
        
        if ipv4_addresses:
            return ipv4_addresses[0]
        return None
    except Exception as e:
        print(f"DNS lookup error: {e}")
        return None

def test_connection_ipv4():
    """Test connection using IPv4 address directly"""
    print("\n" + "="*70)
    print("SUPABASE CONNECTION TEST - IPv4 Direct")
    print("="*70)
    
    # Get IPv4 address
    print(f"Resolving IPv4 address for {HOST}...")
    ipv4 = get_ipv4_address(HOST)
    
    if not ipv4:
        print("[FAILED] Could not resolve IPv4 address")
        print("Trying with hostname anyway...")
        ipv4 = HOST
    
    print(f"Using: {ipv4}:{PORT}")
    print("="*70 + "\n")
    
    try:
        print("Connecting...")
        conn = psycopg2.connect(
            host=ipv4,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            connect_timeout=30  # Longer timeout
        )
        cursor = conn.cursor()
        print("[SUCCESS] Connected!")
        
        # Test query
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"[OK] PostgreSQL: {version[:60]}...")
        
        # Check NBA schema
        cursor.execute('''
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA'
        ''')
        table_count = cursor.fetchone()[0]
        print(f"[OK] NBA schema: {table_count} tables found")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("[SUCCESS] Supabase connection working!")
        print("="*70)
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"\n[FAILED] Connection error: {error_msg}")
        
        if 'timeout' in error_msg.lower():
            print("\nConnection timeout - possible causes:")
            print("1. Firewall blocking outbound connections to port 5432")
            print("2. Windows Defender or antivirus blocking")
            print("3. Network provider blocking database ports")
            print("4. Supabase project not fully initialized")
            
            print("\nTry these solutions:")
            print("- Check Windows Firewall settings")
            print("- Temporarily disable antivirus")
            print("- Try from a different network (mobile hotspot)")
            print("- Check Supabase dashboard for project status")
        
        return False
        
    except Exception as e:
        print(f"\n[FAILED] Error: {e}")
        return False

def test_network_connectivity():
    """Test basic network connectivity"""
    print("\n" + "="*70)
    print("NETWORK CONNECTIVITY TEST")
    print("="*70)
    
    # Test DNS
    try:
        print(f"Testing DNS resolution for {HOST}...")
        addr_info = socket.getaddrinfo(HOST, PORT)
        print(f"[OK] DNS resolved")
        for info in addr_info[:3]:  # Show first 3 addresses
            print(f"  - {info[4][0]} ({'IPv4' if info[0] == socket.AF_INET else 'IPv6'})")
    except Exception as e:
        print(f"[FAILED] DNS: {e}")
        return False
    
    # Test port connectivity (TCP connection test)
    try:
        print(f"\nTesting TCP connection to {HOST}:{PORT}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((HOST, PORT))
        sock.close()
        
        if result == 0:
            print("[OK] Port 5432 is reachable")
            return True
        else:
            print(f"[FAILED] Port 5432 not reachable (error code: {result})")
            print("This indicates a firewall or network block")
            return False
    except Exception as e:
        print(f"[FAILED] Connection test: {e}")
        return False

if __name__ == "__main__":
    # Test network connectivity first
    network_ok = test_network_connectivity()
    
    if network_ok:
        # If network is OK, try database connection
        test_connection_ipv4()
    else:
        print("\n" + "="*70)
        print("NETWORK ISSUE DETECTED")
        print("="*70)
        print("\nThe network test shows port 5432 is blocked or unreachable.")
        print("\nSolutions:")
        print("1. Check Windows Firewall:")
        print("   - Windows Security > Firewall & network protection")
        print("   - Allow an app through firewall")
        print("   - Add Python or allow port 5432")
        print("\n2. Check antivirus software")
        print("3. Try from different network (mobile hotspot)")
        print("4. Contact network administrator")
        print("\n5. Alternative: Use Supabase web dashboard for now:")
        print("   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/editor")















