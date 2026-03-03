"""
Test Different Supabase Pooler Username Formats
"""

import psycopg2

PASSWORD = 'Jcjc1749!!!!'
HOST = 'aws-0-ap-southeast-1.pooler.supabase.com'
PORT = 5432
DATABASE = 'postgres'
PROJECT_ID = 'mxnpfsiyaqqwdcokukij'

# Different username formats to try
USERNAME_FORMATS = [
    f'postgres.{PROJECT_ID}',  # Standard pooler format
    'postgres',  # Direct user
    f'{PROJECT_ID}.postgres',  # Alternative format
    f'postgres@{PROJECT_ID}',  # Alternative format
]

def test_username_format(username):
    """Test connection with specific username format"""
    print(f"\nTesting username format: {username}")
    print("-" * 70)
    
    try:
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=username,
            password=PASSWORD,
            connect_timeout=15
        )
        cursor = conn.cursor()
        print("[SUCCESS] Connected!")
        
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
        
        print(f"\n[SUCCESS] Username format '{username}' works!")
        return True, username
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if 'tenant' in error_msg.lower() or 'user not found' in error_msg.lower():
            print(f"[FAILED] Tenant/user not found")
        elif 'authentication' in error_msg.lower():
            print(f"[FAILED] Authentication failed")
        else:
            print(f"[FAILED] {error_msg[:80]}")
        return False, None
    except Exception as e:
        print(f"[FAILED] {e}")
        return False, None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUPABASE POOLER - USERNAME FORMAT TEST")
    print("="*70)
    print(f"Host: {HOST}:{PORT}")
    print(f"Project ID: {PROJECT_ID}")
    print("="*70)
    
    working_username = None
    
    for username in USERNAME_FORMATS:
        success, username_used = test_username_format(username)
        if success:
            working_username = username_used
            break
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    if working_username:
        print(f"[SUCCESS] Working username format: {working_username}")
        print(f"\nConnection String:")
        print(f"postgresql://{working_username}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
        print("\nUpdate your config files with:")
        print(f"  User: {working_username}")
        print(f"  Host: {HOST}")
        print(f"  Port: {PORT}")
    else:
        print("[FAILED] No username format worked")
        print("\nPossible issues:")
        print("1. Session Pooler not enabled in Supabase dashboard")
        print("2. Project ID might be incorrect")
        print("3. Need to enable pooler in project settings")
        print("\nTo enable Session Pooler:")
        print("1. Go to Supabase Dashboard")
        print("2. Project Settings > Database")
        print("3. Enable 'Connection Pooling'")
        print("4. Select 'Session' mode")
        print("\nOr check the connection string in:")
        print("  Settings > Database > Connection string")
        print("  (Use the 'Session mode' connection string)")















