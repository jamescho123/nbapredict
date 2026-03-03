import psycopg2
import socket

def test_dns():
    print("Testing DNS resolution...")
    hosts = [
        'db.mxnpfsiyaqqwdcokukij.supabase.co',
        'mxnpfsiyaqqwdcokukij.supabase.co'
    ]
    
    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            print(f"[OK] {host} -> {ip}")
        except socket.gaierror as e:
            print(f"[FAIL] {host} -> DNS lookup failed: {e}")

def test_connection():
    print("\nTesting Supabase connection...")
    
    configs = [
        {
            'name': 'Direct Connection',
            'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'VXUXqY9Uofg9ujoo',
            'port': 5432
        },
        {
            'name': 'Connection Pooler',
            'host': 'mxnpfsiyaqqwdcokukij.supabase.co',
            'database': 'postgres',
            'user': 'postgres.mxnpfsiyaqqwdcokukij',
            'password': 'VXUXqY9Uofg9ujoo',
            'port': 6543
        }
    ]
    
    for config in configs:
        try:
            name = config.pop('name')
            print(f"\nTrying {name}...")
            conn = psycopg2.connect(**config, connect_timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"[OK] Connected successfully!")
            print(f"  PostgreSQL version: {version[:50]}...")
            conn.close()
            return True
        except Exception as e:
            print(f"[FAIL] Failed: {e}")
    
    return False

if __name__ == "__main__":
    print("=== Supabase Connection Test ===\n")
    test_dns()
    success = test_connection()
    
    if not success:
        print("\n=== Troubleshooting ===")
        print("1. Check your internet connection")
        print("2. Verify the project URL in Supabase dashboard")
        print("3. Check if your IP is allowed in Supabase network settings")
        print("4. Verify the database password is correct")
        print("\nAlternative: Use pg_dump/pg_restore method")
        print("  python export_to_sql.py")
        print("  Then upload the SQL file to Supabase")

