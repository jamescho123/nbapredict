import os
import subprocess
import sys

def install_pgvector():
    """Install pgvector extension on Windows using the method from programmer.ie"""
    
    # Check if PostgreSQL is installed
    print("Checking PostgreSQL installation...")
    pg_path = input("Enter your PostgreSQL installation path (e.g. C:\\Program Files\\PostgreSQL\\17): ")
    
    if not os.path.exists(pg_path):
        print(f"Error: Path {pg_path} does not exist.")
        return False
    
    # Set PGROOT environment variable
    os.environ["PGROOT"] = pg_path
    print(f"Set PGROOT to {pg_path}")
    
    # Check if we're already in the pgvector directory
    current_dir = os.getcwd()
    if os.path.basename(current_dir) == "pgvector":
        pgvector_dir = current_dir
    else:
        pgvector_dir = os.path.join(current_dir, "pgvector")
    
    # Compile pgvector
    print("Compiling pgvector...")
    try:
        subprocess.run(["nmake", "/F", "Makefile.win"], cwd=pgvector_dir, check=True)
        subprocess.run(["nmake", "/F", "Makefile.win", "install"], cwd=pgvector_dir, check=True)
        print("pgvector compiled and installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")
        return False
    except FileNotFoundError:
        print("Error: nmake not found. Make sure Visual Studio with C++ build tools is installed.")
        return False
    
    print("\nNext steps:")
    print("1. Connect to PostgreSQL and run: CREATE EXTENSION vector;")
    print("2. Verify installation with: SELECT * FROM pg_available_extensions WHERE name = 'vector';")
    
    return True

if __name__ == "__main__":
    install_pgvector() 