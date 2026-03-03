import subprocess
import os
from datetime import datetime

def export_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"nba_database_export_{timestamp}.sql"
    
    print(f"Exporting database to {output_file}...")
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = 'jcjc1749'
    
    # pg_dump command
    cmd = [
        'pg_dump',
        '-h', 'localhost',
        '-U', 'postgres',
        '-d', 'James',
        '-n', 'NBA',
        '-F', 'p',
        '-f', output_file
    ]
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[OK] Export successful: {output_file}")
            print(f"\nNext steps:")
            print(f"1. Open Supabase SQL Editor: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new")
            print(f"2. Copy contents of {output_file}")
            print(f"3. Paste and execute in SQL Editor")
            print(f"\nOr use psql:")
            print(f"  $env:PGPASSWORD='VXUXqY9Uofg9ujoo'")
            print(f"  psql -h db.mxnpfsiyaqqwdcokukij.supabase.co -U postgres -d postgres -f {output_file}")
        else:
            print(f"[FAIL] Export failed: {result.stderr}")
            print(f"\nMake sure PostgreSQL client tools are installed:")
            print(f"  https://www.postgresql.org/download/windows/")
    except FileNotFoundError:
        print("[FAIL] pg_dump not found in PATH")
        print("\nInstall PostgreSQL client tools:")
        print("  https://www.postgresql.org/download/windows/")
        print("\nOr use manual export method (see manual_export.py)")

if __name__ == "__main__":
    export_database()

