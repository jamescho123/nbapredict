import subprocess
import sys
import os

def check_postgres_service():
    """Check if PostgreSQL service is running"""
    print("===== PostgreSQL Service Check =====")
    print()
    
    try:
        # Check if PostgreSQL service is running using sc query
        print("Checking PostgreSQL service status...")
        result = subprocess.run(['sc', 'query', 'postgresql-x64-17'], 
                               capture_output=True, text=True)
        
        if "RUNNING" in result.stdout:
            print("PostgreSQL service is RUNNING")
            return True
        else:
            print("PostgreSQL service is NOT running or has a different name")
            print("\nOutput from sc query:")
            print(result.stdout)
            
            # Try to find PostgreSQL services
            print("\nSearching for PostgreSQL services...")
            services = subprocess.run(['sc', 'query', 'state=', 'all'], 
                                    capture_output=True, text=True)
            
            # Filter for PostgreSQL related services
            pg_services = []
            for line in services.stdout.splitlines():
                if "SERVICE_NAME" in line and ("post" in line.lower() or "pg" in line.lower()):
                    pg_services.append(line.strip())
            
            if pg_services:
                print("\nFound potential PostgreSQL services:")
                for svc in pg_services:
                    print(f"  {svc}")
                print("\nYou can try to start the service with:")
                print(f"  net start {pg_services[0].split(':')[1].strip()}")
            else:
                print("\nNo PostgreSQL services found.")
                print("PostgreSQL might not be installed or the service name is different.")
            
            return False
    except Exception as e:
        print(f"Error checking service: {e}")
        return False

def try_psql_connection():
    """Try to connect using psql command"""
    print("\n===== Testing psql connection =====")
    
    try:
        # Check if psql is in the path
        psql_paths = [
            r"C:\Program Files\PostgreSQL\17\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\13\bin\psql.exe"
        ]
        
        psql_path = None
        for path in psql_paths:
            if os.path.exists(path):
                psql_path = path
                print(f"Found psql at: {psql_path}")
                break
        
        if not psql_path:
            print("Could not find psql executable.")
            return False
        
        # Try connecting to PostgreSQL with version command
        print("\nTrying to get PostgreSQL version...")
        os.environ["PGPASSWORD"] = "jcjc1749"
        result = subprocess.run([psql_path, "-h", "localhost", "-U", "postgres", 
                                "-d", "postgres", "-c", "SELECT version();"],
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Successfully connected to PostgreSQL!")
            print(f"Version info: {result.stdout.strip()}")
            return True
        else:
            print("Failed to connect to PostgreSQL")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"Error during connection test: {e}")
        return False
    finally:
        # Clear password from environment
        if "PGPASSWORD" in os.environ:
            del os.environ["PGPASSWORD"]

if __name__ == "__main__":
    service_running = check_postgres_service()
    
    if service_running:
        connection_ok = try_psql_connection()
    else:
        print("\nPlease start the PostgreSQL service before testing the connection.")
        connection_ok = False
    
    print("\nPress Enter to exit...", end="")
    input()
    sys.exit(0 if (service_running and connection_ok) else 1) 