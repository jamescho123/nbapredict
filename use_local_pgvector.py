import os
import shutil
import sys

def use_local_pgvector():
    """Use pgvector files from the local project"""
    print("===== Using Local pgvector Files =====")
    print()
    
    # Set paths
    pg_path = r"C:\Program Files\PostgreSQL\17"
    project_dir = os.getcwd()
    pgvector_dir = os.path.join(project_dir, "pgvector")
    
    # Check if pgvector directory exists
    if not os.path.exists(pgvector_dir):
        print(f"Error: pgvector directory not found at {pgvector_dir}")
        return False
    
    # Check if PostgreSQL directory exists
    if not os.path.exists(pg_path):
        print(f"Error: PostgreSQL directory {pg_path} does not exist.")
        return False
    
    # Create directories if they don't exist
    lib_dir = os.path.join(pg_path, "lib")
    ext_dir = os.path.join(pg_path, "share", "extension")
    
    os.makedirs(lib_dir, exist_ok=True)
    os.makedirs(ext_dir, exist_ok=True)
    
    # Copy vector.control
    control_src = os.path.join(pgvector_dir, "vector.control")
    control_dst = os.path.join(ext_dir, "vector.control")
    
    if os.path.exists(control_src):
        print(f"Copying {control_src} to {control_dst}")
        try:
            shutil.copy2(control_src, control_dst)
            print("Successfully copied vector.control")
        except Exception as e:
            print(f"Error copying vector.control: {e}")
            print("Try running this script as administrator")
            return False
    else:
        print(f"Warning: vector.control not found at {control_src}")
    
    # Copy SQL files
    sql_dir = os.path.join(pgvector_dir, "sql")
    
    if os.path.exists(sql_dir):
        print(f"Copying SQL files from {sql_dir} to {ext_dir}")
        try:
            for file in os.listdir(sql_dir):
                if file.endswith(".sql"):
                    src_file = os.path.join(sql_dir, file)
                    dst_file = os.path.join(ext_dir, file)
                    shutil.copy2(src_file, dst_file)
            print("Successfully copied SQL files")
        except Exception as e:
            print(f"Error copying SQL files: {e}")
            print("Try running this script as administrator")
            return False
    else:
        print(f"Warning: SQL directory not found at {sql_dir}")
    
    # Check for vector.dll in src directory
    dll_src = os.path.join(pgvector_dir, "src", "vector.dll")
    dll_dst = os.path.join(lib_dir, "vector.dll")
    
    if os.path.exists(dll_src):
        print(f"Copying {dll_src} to {dll_dst}")
        try:
            shutil.copy2(dll_src, dll_dst)
            print("Successfully copied vector.dll")
        except Exception as e:
            print(f"Error copying vector.dll: {e}")
            print("Try running this script as administrator")
            return False
    else:
        print(f"Warning: vector.dll not found at {dll_src}")
        print("The vector.dll file is required but was not found.")
        print("You need to compile it or download a pre-built version.")
    
    # List all files in pgvector directory to help find vector.dll
    print("\nSearching for vector.dll in pgvector directory...")
    for root, dirs, files in os.walk(pgvector_dir):
        for file in files:
            if file == "vector.dll":
                dll_path = os.path.join(root, file)
                print(f"Found vector.dll at {dll_path}")
                try:
                    shutil.copy2(dll_path, dll_dst)
                    print(f"Copied {dll_path} to {dll_dst}")
                    break
                except Exception as e:
                    print(f"Error copying vector.dll: {e}")
    
    print("\nNext steps:")
    print("1. If vector.dll was not found, you need to compile it or download a pre-built version.")
    print("2. Restart PostgreSQL service:")
    print("   - Open Services (Run → services.msc)")
    print("   - Find postgresql-x64-17")
    print("   - Right-click and select 'Restart'")
    print("3. Connect to your database and run:")
    print("   CREATE EXTENSION vector;")
    print()
    
    return True

if __name__ == "__main__":
    use_local_pgvector()
    input("Press Enter to exit...") 