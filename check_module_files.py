import os

def check_module_files():
    """Check if the pgvector module files are in the correct PostgreSQL lib directory"""
    
    # Get PostgreSQL installation path
    pg_path = input("Enter your PostgreSQL installation path (e.g. C:\\Program Files\\PostgreSQL\\17): ")
    
    if not os.path.exists(pg_path):
        print(f"Error: Path {pg_path} does not exist.")
        return False
    
    # Define directories to check
    pg_lib_dir = os.path.join(pg_path, "lib")
    
    if not os.path.exists(pg_lib_dir):
        print(f"Error: Lib directory not found at {pg_lib_dir}")
        return False
    
    # Check for vector.dll or vector.so
    vector_dll = os.path.join(pg_lib_dir, "vector.dll")
    vector_so = os.path.join(pg_lib_dir, "vector.so")
    
    if os.path.exists(vector_dll):
        print(f"Found vector.dll at {vector_dll}")
        print(f"Size: {os.path.getsize(vector_dll)} bytes")
        print(f"Last modified: {os.path.getmtime(vector_dll)}")
    elif os.path.exists(vector_so):
        print(f"Found vector.so at {vector_so}")
        print(f"Size: {os.path.getsize(vector_so)} bytes")
        print(f"Last modified: {os.path.getmtime(vector_so)}")
    else:
        print(f"Error: Neither vector.dll nor vector.so found in {pg_lib_dir}")
        
        # Check if there are any files with "vector" in the name
        vector_files = [f for f in os.listdir(pg_lib_dir) if "vector" in f.lower()]
        if vector_files:
            print("\nFound files with 'vector' in the name:")
            for file in vector_files:
                print(f"- {file}")
        else:
            print("\nNo files with 'vector' in the name found in the lib directory.")
            
        # Check if we have the source files in the project
        project_dir = os.getcwd()
        pgvector_dir = os.path.join(project_dir, "pgvector")
        pgvector_src_dir = os.path.join(pgvector_dir, "src")
        
        if os.path.exists(pgvector_src_dir):
            print(f"\nFound pgvector source directory at {pgvector_src_dir}")
            print("Source files found:")
            for file in os.listdir(pgvector_src_dir):
                if file.endswith(".c") or file.endswith(".h"):
                    print(f"- {file}")
        else:
            print(f"\nNo pgvector source directory found at {pgvector_src_dir}")
    
    return True

if __name__ == "__main__":
    check_module_files() 