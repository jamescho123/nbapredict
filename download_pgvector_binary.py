import os
import subprocess
import tempfile
import zipfile
import shutil
import sys
import webbrowser

def download_pgvector_binary():
    """Download a pre-compiled pgvector binary for PostgreSQL 17 on Windows"""
    print("===== Download Pre-compiled pgvector Binary =====")
    print()
    
    # Direct download link for pgvector binary
    pgvector_url = "https://github.com/pgvector/pgvector/releases/download/v0.8.0/vector-0.8.0-pg17-windows-x86_64.zip"
    
    # Create a temporary directory
    temp_dir = tempfile.gettempdir()
    zip_path = os.path.join(temp_dir, "pgvector.zip")
    extract_dir = os.path.join(temp_dir, "pgvector_extract")
    
    # PostgreSQL path
    pg_path = r"C:\Program Files\PostgreSQL\17"
    
    # Check if PostgreSQL directory exists
    if not os.path.exists(pg_path):
        print(f"Error: PostgreSQL directory {pg_path} does not exist.")
        return False
    
    print(f"Downloading pgvector binary to {zip_path}...")
    print("This may take a moment...")
    
    try:
        # Use PowerShell to download the file
        download_cmd = f'powershell -Command "& {{[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri \'{pgvector_url}\' -OutFile \'{zip_path}\'}}"'
        subprocess.run(download_cmd, shell=True, check=True)
        print("Download complete!")
    except Exception as e:
        print(f"Error downloading pgvector binary: {e}")
        print("\nAlternative: Download manually from the following URL:")
        print("https://github.com/pgvector/pgvector/releases/tag/v0.8.0")
        print("File name: vector-0.8.0-pg17-windows-x86_64.zip")
        webbrowser.open("https://github.com/pgvector/pgvector/releases/tag/v0.8.0")
        return False
    
    # Create extract directory if it doesn't exist
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)
    
    # Extract the ZIP file
    print(f"Extracting ZIP file to {extract_dir}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print("Extraction complete!")
    except Exception as e:
        print(f"Error extracting ZIP file: {e}")
        return False
    
    # Copy files to PostgreSQL directories
    print("\nCopying files to PostgreSQL directories...")
    
    # Create directories if they don't exist
    lib_dir = os.path.join(pg_path, "lib")
    ext_dir = os.path.join(pg_path, "share", "extension")
    
    os.makedirs(lib_dir, exist_ok=True)
    os.makedirs(ext_dir, exist_ok=True)
    
    # Copy vector.dll
    dll_src = os.path.join(extract_dir, "vector.dll")
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
        print(f"Error: vector.dll not found in extracted files at {dll_src}")
        return False
    
    # Copy vector.control
    control_src = os.path.join(extract_dir, "vector.control")
    control_dst = os.path.join(ext_dir, "vector.control")
    
    if os.path.exists(control_src):
        print(f"Copying {control_src} to {control_dst}")
        try:
            shutil.copy2(control_src, control_dst)
            print("Successfully copied vector.control")
        except Exception as e:
            print(f"Error copying vector.control: {e}")
            return False
    else:
        print(f"Error: vector.control not found in extracted files at {control_src}")
        return False
    
    # Copy SQL files
    print("Copying SQL files...")
    try:
        for file in os.listdir(extract_dir):
            if file.endswith(".sql"):
                src_file = os.path.join(extract_dir, file)
                dst_file = os.path.join(ext_dir, file)
                shutil.copy2(src_file, dst_file)
        print("Successfully copied SQL files")
    except Exception as e:
        print(f"Error copying SQL files: {e}")
        return False
    
    # Clean up
    try:
        os.remove(zip_path)
        shutil.rmtree(extract_dir)
    except:
        pass
    
    print("\n===== Installation Complete! =====")
    print("pgvector files have been installed.")
    print()
    print("Next steps:")
    print("1. Restart PostgreSQL service:")
    print("   - Open Services (Run → services.msc)")
    print("   - Find postgresql-x64-17")
    print("   - Right-click and select 'Restart'")
    print()
    print("2. Connect to your database and run:")
    print("   CREATE EXTENSION vector;")
    print()
    
    return True

if __name__ == "__main__":
    download_pgvector_binary()
    input("Press Enter to exit...") 