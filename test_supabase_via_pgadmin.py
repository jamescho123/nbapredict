"""
Test if Supabase connection will work for pgAdmin 4
This uses the same connection method pgAdmin would use
"""

import psycopg2
import ssl

print("=" * 70)
print("Testing Supabase Connection for pgAdmin 4")
print("=" * 70)
print()

# Connection parameters (same as pgAdmin would use)
configs = [
    {
        'name': 'Direct Connection (port 5432)',
        'host': 'db.mxnpfsiyaqqwdcokukij.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'VXUXqY9Uofg9ujoo',
        'connect_timeout': 10,
        'sslmode': 'require'
    },
    {
        'name': 'Connection Pooler (port 6543)',
        'host': 'mxnpfsiyaqqwdcokukij.supabase.co',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.mxnpfsiyaqqwdcokukij',
        'password': 'VXUXqY9Uofg9ujoo',
        'connect_timeout': 10,
        'sslmode': 'require'
    }
]

success = False
working_config = None

for config in configs:
    name = config.pop('name')
    print(f"Testing: {name}")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  User: {config['user']}")
    print()
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Check for NBA schema
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.schemata 
            WHERE schema_name = 'NBA';
        """)
        has_nba = cursor.fetchone()[0] > 0
        
        print(f"  [OK] CONNECTION SUCCESSFUL!")
        print(f"  PostgreSQL: {version.split(',')[0]}")
        print(f"  NBA schema exists: {'Yes' if has_nba else 'No (will be created on import)'}")
        print()
        
        if has_nba:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'NBA'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"  Found {len(tables)} existing tables in NBA schema")
            if len(tables) > 0:
                print(f"  Tables: {', '.join([t[0] for t in tables[:5]])}{'...' if len(tables) > 5 else ''}")
        
        conn.close()
        success = True
        working_config = (name, config)
        break
        
    except psycopg2.OperationalError as e:
        print(f"  [FAIL] CONNECTION FAILED")
        print(f"  Error: {str(e)[:100]}")
        print()
    except Exception as e:
        print(f"  [FAIL] UNEXPECTED ERROR")
        print(f"  Error: {str(e)[:100]}")
        print()

print("=" * 70)
if success:
    print("RESULT: pgAdmin 4 connection will work!")
    print("=" * 70)
    print()
    print("pgAdmin 4 Setup Instructions:")
    print("-" * 70)
    print("1. Open pgAdmin 4")
    print("2. Right-click 'Servers' → 'Register' → 'Server'")
    print()
    print("3. Fill in:")
    print(f"   General Tab:")
    print(f"     Name: Supabase - NBA_Predict")
    print()
    print(f"   Connection Tab:")
    name, cfg = working_config
    print(f"     Host: {cfg['host']}")
    print(f"     Port: {cfg['port']}")
    print(f"     Database: {cfg['database']}")
    print(f"     Username: {cfg['user']}")
    print(f"     Password: {cfg['password']}")
    print(f"     Save password: Yes (check the box)")
    print()
    print(f"   SSL Tab:")
    print(f"     SSL mode: Require")
    print()
    print("4. Click 'Save'")
    print()
    print("5. Import database:")
    print("   - Right-click 'postgres' → 'Query Tool'")
    print("   - Open file: nba_manual_export_20251024_201041.sql")
    print("   - Execute (F5)")
    print()
    print("See PGADMIN_SUPABASE_GUIDE.md for detailed instructions")
    
else:
    print("RESULT: Connection Failed - Network is blocking PostgreSQL ports")
    print("=" * 70)
    print()
    print("Your network is blocking both:")
    print("  - Port 5432 (direct connection)")
    print("  - Port 6543 (connection pooler)")
    print()
    print("Solutions:")
    print("1. Use Supabase Web Interface (RECOMMENDED)")
    print("   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new")
    print("   - Copy contents of nba_manual_export_20251024_201041.sql")
    print("   - Paste and execute in SQL editor")
    print()
    print("2. Configure Firewall")
    print("   - Allow outbound connections to *.supabase.co on ports 5432, 6543")
    print()
    print("3. Use VPN")
    print("   - Connect to VPN that doesn't block PostgreSQL ports")
    print()
    print("See FINAL_SOLUTION.md for more details")

print()

