import os
import shutil
import sys

def main():
    print("===== Copy pgvector Files =====")
    print()
    
    # Set paths
    pg_path = r"C:\Program Files\PostgreSQL\17"
    src_dir = r"C:\Users\hp\Downloads\pgvector-master"
    
    # Check if source directory exists
    if not os.path.exists(src_dir):
        print(f"Error: Source directory {src_dir} does not exist.")
        print("Please extract pgvector-master.zip first.")
        return
    
    # Check if PostgreSQL directory exists
    if not os.path.exists(pg_path):
        print(f"Error: PostgreSQL directory {pg_path} does not exist.")
        return
    
    # Create extension directories if they don't exist
    ext_dir = os.path.join(pg_path, "share", "extension")
    lib_dir = os.path.join(pg_path, "lib")
    
    os.makedirs(ext_dir, exist_ok=True)
    os.makedirs(lib_dir, exist_ok=True)
    
    # Copy control file
    control_src = os.path.join(src_dir, "vector.control")
    control_dst = os.path.join(ext_dir, "vector.control")
    
    if os.path.exists(control_src):
        print(f"Copying {control_src} to {control_dst}")
        try:
            shutil.copy2(control_src, control_dst)
            print("Successfully copied vector.control")
        except Exception as e:
            print(f"Error copying vector.control: {e}")
            print("Try running this script as administrator")
    else:
        print(f"Warning: vector.control not found at {control_src}")
    
    # Copy SQL files
    sql_src_dir = os.path.join(src_dir, "sql")
    
    if os.path.exists(sql_src_dir):
        print(f"Copying SQL files from {sql_src_dir} to {ext_dir}")
        try:
            for file in os.listdir(sql_src_dir):
                if file.endswith(".sql"):
                    src_file = os.path.join(sql_src_dir, file)
                    dst_file = os.path.join(ext_dir, file)
                    shutil.copy2(src_file, dst_file)
            print("Successfully copied SQL files")
        except Exception as e:
            print(f"Error copying SQL files: {e}")
            print("Try running this script as administrator")
    else:
        print(f"Warning: SQL directory not found at {sql_src_dir}")
    
    # Check for vector.dll
    dll_src = os.path.join(src_dir, "vector.dll")
    dll_dst = os.path.join(lib_dir, "vector.dll")
    
    if os.path.exists(dll_src):
        print(f"Copying {dll_src} to {dll_dst}")
        try:
            shutil.copy2(dll_src, dll_dst)
            print("Successfully copied vector.dll")
        except Exception as e:
            print(f"Error copying vector.dll: {e}")
            print("Try running this script as administrator")
    else:
        print(f"Warning: vector.dll not found at {dll_src}")
        print("The vector.dll file is required but needs to be compiled.")
        print("Without this file, the pgvector extension will not work.")
    
    print()
    print("File copying complete. Check the messages above for any errors.")
    print()
    print("Next steps:")
    print("1. If vector.dll was not found, you need to compile it or download a pre-built version.")
    print("2. Restart PostgreSQL service:")
    print("   - Open Services (Run → services.msc)")
    print("   - Find postgresql-x64-17")
    print("   - Right-click and select 'Restart'")
    print("3. Connect to your database and run:")
    print("   CREATE EXTENSION vector;")
    print()

if __name__ == "__main__":
    main()
    input("Press Enter to exit...") 