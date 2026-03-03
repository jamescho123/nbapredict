import os
import subprocess
import sys
import shutil
import tempfile
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def find_vs_dev_cmd():
    """Find VsDevCmd.bat in the system"""
    possible_paths = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat",
        r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat",
        r"C:\Program Files\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\Tools\VsDevCmd.bat",
        r"C:\Program Files\Microsoft Visual Studio\2019\Community\Common7\Tools\VsDevCmd.bat"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If not found in common locations, try to search for it
    try:
        result = subprocess.run(["where", "/r", "C:\\", "VsDevCmd.bat"], 
                               capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout:
            paths = result.stdout.strip().split('\n')
            if paths:
                return paths[0]
    except:
        pass
    
    return None

def compile_pgvector():
    """Compile pgvector from source"""
    print("===== Compile pgvector from Source =====")
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
    
    # Find VsDevCmd.bat
    vs_dev_cmd = find_vs_dev_cmd()
    if not vs_dev_cmd:
        print("Error: VsDevCmd.bat not found. Make sure Visual Studio Build Tools is installed.")
        return False
    
    print(f"Found VsDevCmd.bat at: {vs_dev_cmd}")
    
    # Create a batch file to set up the environment and compile pgvector
    temp_dir = tempfile.gettempdir()
    batch_file = os.path.join(temp_dir, "compile_pgvector.bat")
    
    with open(batch_file, "w") as f:
        f.write("@echo off\n")
        f.write(f'call "{vs_dev_cmd}" -arch=x64\n')
        f.write(f'cd /d "{pgvector_dir}"\n')
        f.write(f'set PATH={pg_path}\\bin;%PATH%\n')
        f.write("set USE_PGXS=1\n")
        f.write(f'set PGWIN_DEPS={pg_path}\n')
        f.write(f'set PGROOT={pg_path}\n')  # Add PGROOT environment variable
        f.write("nmake /f Makefile.win\n")
        f.write("if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%\n")
        f.write(f'echo vector.dll location: > "{temp_dir}\\vector_dll_path.txt"\n')
        f.write(f'dir /b /s vector.dll >> "{temp_dir}\\vector_dll_path.txt"\n')
    
    print("Running compilation...")
    result = subprocess.run([batch_file], shell=True)
    
    if result.returncode != 0:
        print("Error: Compilation failed.")
        return False
    
    print("Compilation successful!")
    
    # Find vector.dll
    vector_dll_path = None
    try:
        with open(os.path.join(temp_dir, "vector_dll_path.txt"), "r") as f:
            lines = f.readlines()
            for line in lines[1:]:  # Skip the first line which is the header
                if "vector.dll" in line:
                    vector_dll_path = line.strip()
                    break
    except:
        pass
    
    if not vector_dll_path:
        vector_dll_path = os.path.join(pgvector_dir, "vector.dll")
    
    if not os.path.exists(vector_dll_path):
        print(f"Error: vector.dll not found at {vector_dll_path}")
        return False
    
    print(f"Found vector.dll at: {vector_dll_path}")
    
    # Copy files if running as admin
    if is_admin():
        print("Running as administrator, copying files...")
        
        # Create directories if they don't exist
        lib_dir = os.path.join(pg_path, "lib")
        ext_dir = os.path.join(pg_path, "share", "extension")
        
        os.makedirs(lib_dir, exist_ok=True)
        os.makedirs(ext_dir, exist_ok=True)
        
        # Copy vector.dll
        try:
            shutil.copy2(vector_dll_path, os.path.join(lib_dir, "vector.dll"))
            print(f"Copied vector.dll to {lib_dir}")
        except Exception as e:
            print(f"Error copying vector.dll: {e}")
            return False
        
        # Copy vector.control
        try:
            shutil.copy2(os.path.join(pgvector_dir, "vector.control"), 
                        os.path.join(ext_dir, "vector.control"))
            print(f"Copied vector.control to {ext_dir}")
        except Exception as e:
            print(f"Error copying vector.control: {e}")
            return False
        
        # Copy SQL files
        try:
            sql_dir = os.path.join(pgvector_dir, "sql")
            for file in os.listdir(sql_dir):
                if file.endswith(".sql"):
                    shutil.copy2(os.path.join(sql_dir, file), 
                                os.path.join(ext_dir, file))
            print(f"Copied SQL files to {ext_dir}")
        except Exception as e:
            print(f"Error copying SQL files: {e}")
            return False
        
        print("\nAll files copied successfully!")
        print("\nNext steps:")
        print("1. Restart PostgreSQL service:")
        print("   - Open Services (Run → services.msc)")
        print("   - Find postgresql-x64-17")
        print("   - Right-click and select 'Restart'")
        print("\n2. Connect to your database and run:")
        print("   CREATE EXTENSION vector;")
    else:
        print("\nNot running as administrator. Files need to be copied manually.")
        print("\nNext steps:")
        print("1. Copy the following files:")
        print(f"   - Copy {vector_dll_path} to {pg_path}\\lib\\")
        print(f"   - Copy {pgvector_dir}\\vector.control to {pg_path}\\share\\extension\\")
        print(f"   - Copy all SQL files from {pgvector_dir}\\sql\\ to {pg_path}\\share\\extension\\")
        print("\n2. Restart PostgreSQL service:")
        print("   - Open Services (Run → services.msc)")
        print("   - Find postgresql-x64-17")
        print("   - Right-click and select 'Restart'")
        print("\n3. Connect to your database and run:")
        print("   CREATE EXTENSION vector;")
        
        # Create a batch file to copy the files
        copy_batch = os.path.join(project_dir, "copy_pgvector_files.bat")
        with open(copy_batch, "w") as f:
            f.write("@echo off\n")
            f.write("echo ===== Copy pgvector Files =====\n")
            f.write("echo.\n")
            f.write("REM Check for admin privileges\n")
            f.write("net session >nul 2>&1\n")
            f.write("if %ERRORLEVEL% NEQ 0 (\n")
            f.write("    echo Error: This script requires administrator privileges.\n")
            f.write("    echo Please right-click on this script and select \"Run as administrator\".\n")
            f.write("    pause\n")
            f.write("    exit /b 1\n")
            f.write(")\n\n")
            f.write("REM Set paths\n")
            f.write(f'set PG_PATH={pg_path}\n')
            f.write(f'set VECTOR_DLL={vector_dll_path}\n')
            f.write(f'set PGVECTOR_DIR={pgvector_dir}\n\n')
            f.write("REM Create directories if they don't exist\n")
            f.write('if not exist "%PG_PATH%\\lib" mkdir "%PG_PATH%\\lib"\n')
            f.write('if not exist "%PG_PATH%\\share\\extension" mkdir "%PG_PATH%\\share\\extension"\n\n')
            f.write("REM Copy vector.dll\n")
            f.write('echo Copying vector.dll to %PG_PATH%\\lib\\\n')
            f.write('copy /Y "%VECTOR_DLL%" "%PG_PATH%\\lib\\"\n')
            f.write("if %ERRORLEVEL% NEQ 0 (\n")
            f.write("    echo Error: Failed to copy vector.dll\n")
            f.write("    pause\n")
            f.write("    exit /b 1\n")
            f.write(")\n\n")
            f.write("REM Copy vector.control\n")
            f.write('echo Copying vector.control to %PG_PATH%\\share\\extension\\\n')
            f.write('copy /Y "%PGVECTOR_DIR%\\vector.control" "%PG_PATH%\\share\\extension\\"\n')
            f.write("if %ERRORLEVEL% NEQ 0 (\n")
            f.write("    echo Error: Failed to copy vector.control\n")
            f.write("    pause\n")
            f.write("    exit /b 1\n")
            f.write(")\n\n")
            f.write("REM Copy SQL files\n")
            f.write('echo Copying SQL files to %PG_PATH%\\share\\extension\\\n')
            f.write('copy /Y "%PGVECTOR_DIR%\\sql\\*.sql" "%PG_PATH%\\share\\extension\\"\n')
            f.write("if %ERRORLEVEL% NEQ 0 (\n")
            f.write("    echo Error: Failed to copy SQL files\n")
            f.write("    pause\n")
            f.write("    exit /b 1\n")
            f.write(")\n\n")
            f.write("echo.\n")
            f.write("echo Files copied successfully!\n")
            f.write("echo.\n")
            f.write("echo Next steps:\n")
            f.write("echo 1. Restart PostgreSQL service:\n")
            f.write("echo    - Open Services (Run → services.msc)\n")
            f.write("echo    - Find postgresql-x64-17\n")
            f.write("echo    - Right-click and select \"Restart\"\n")
            f.write("echo.\n")
            f.write("echo 2. Connect to your database and run:\n")
            f.write("echo    CREATE EXTENSION vector;\n")
            f.write("echo.\n")
            f.write("pause\n")
        
        print(f"\nCreated batch file: {copy_batch}")
        print("Run this batch file as administrator to copy the files.")
    
    return True

if __name__ == "__main__":
    compile_pgvector()
    input("\nPress Enter to exit...") 