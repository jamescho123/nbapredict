import os
import subprocess

def check_extension_files():
    """Check if the pgvector files are in the correct PostgreSQL directories"""
    
    # Get PostgreSQL installation path
    pg_path = input("Enter your PostgreSQL installation path (e.g. C:\\Program Files\\PostgreSQL\\17): ")
    
    if not os.path.exists(pg_path):
        print(f"Error: Path {pg_path} does not exist.")
        return False
    
    # Define directories to check
    pg_ext_dir = os.path.join(pg_path, "share", "extension")
    
    if not os.path.exists(pg_ext_dir):
        print(f"Error: Extension directory not found at {pg_ext_dir}")
        return False
    
    # Check for vector.control
    vector_control = os.path.join(pg_ext_dir, "vector.control")
    if os.path.exists(vector_control):
        print(f"Found vector.control at {vector_control}")
        
        # Show content of vector.control
        try:
            with open(vector_control, 'r') as f:
                content = f.read()
                print("\nContent of vector.control:")
                print(content)
        except Exception as e:
            print(f"Error reading vector.control: {e}")
    else:
        print(f"Error: vector.control not found at {vector_control}")
    
    # Check for vector.sql
    vector_sql = os.path.join(pg_ext_dir, "vector.sql")
    if os.path.exists(vector_sql):
        print(f"\nFound vector.sql at {vector_sql}")
        
        # Show first few lines of vector.sql
        try:
            with open(vector_sql, 'r') as f:
                lines = f.readlines()[:10]  # First 10 lines
                print("\nFirst few lines of vector.sql:")
                for line in lines:
                    print(line.strip())
                print("...")
        except Exception as e:
            print(f"Error reading vector.sql: {e}")
    else:
        print(f"Error: vector.sql not found at {vector_sql}")
    
    # Check for version upgrade files
    print("\nChecking for version upgrade files:")
    version_files_found = False
    for file in os.listdir(pg_ext_dir):
        if file.startswith("vector--") and file.endswith(".sql"):
            version_files_found = True
            print(f"Found {file}")
    
    if not version_files_found:
        print("No version upgrade files found.")
    
    return True

if __name__ == "__main__":
    check_extension_files() 