import os
import subprocess
import sys

def check_vs_installation():
    """Check if Visual Studio with C++ is installed"""
    print("===== Checking Visual Studio C++ Installation =====")
    print()
    
    # Check for possible Visual Studio installation paths
    vs_paths = [
        r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community",
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional",
        r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise"
    ]
    
    found_vs = False
    for path in vs_paths:
        if os.path.exists(path):
            print(f"Found Visual Studio installation at: {path}")
            found_vs = True
            
            # Check for C++ components
            msvc_path = os.path.join(path, "VC", "Tools", "MSVC")
            if os.path.exists(msvc_path):
                print(f"Found MSVC tools at: {msvc_path}")
                print("C++ components are installed!")
            else:
                print(f"MSVC tools not found at: {msvc_path}")
                print("C++ components may not be installed.")
    
    if not found_vs:
        print("No Visual Studio installation found.")
        print("Please install Visual Studio with C++ build tools.")
        return False
    
    # Check for nmake
    print("\nChecking for nmake...")
    try:
        result = subprocess.run(["where", "nmake"], capture_output=True, text=True)
        if result.returncode == 0:
            nmake_path = result.stdout.strip()
            print(f"Found nmake at: {nmake_path}")
        else:
            print("nmake not found in PATH.")
            print("Visual Studio environment is not set up correctly.")
            
            # Try to find nmake directly
            for path in vs_paths:
                if os.path.exists(path):
                    nmake_candidates = []
                    for root, dirs, files in os.walk(path):
                        if "nmake.exe" in files:
                            nmake_candidates.append(os.path.join(root, "nmake.exe"))
                    
                    if nmake_candidates:
                        print("\nFound nmake.exe in Visual Studio directories:")
                        for candidate in nmake_candidates:
                            print(f"  {candidate}")
                        print("\nYou need to set up the Visual Studio environment before using nmake.")
                        print("Run the Developer Command Prompt for Visual Studio or use VsDevCmd.bat")
    except Exception as e:
        print(f"Error checking for nmake: {e}")
    
    # Check for cl.exe (C++ compiler)
    print("\nChecking for C++ compiler (cl.exe)...")
    try:
        result = subprocess.run(["where", "cl"], capture_output=True, text=True)
        if result.returncode == 0:
            cl_path = result.stdout.strip()
            print(f"Found C++ compiler at: {cl_path}")
        else:
            print("C++ compiler (cl.exe) not found in PATH.")
            print("Visual Studio environment is not set up correctly.")
            
            # Try to find cl.exe directly
            for path in vs_paths:
                if os.path.exists(path):
                    cl_candidates = []
                    for root, dirs, files in os.walk(path):
                        if "cl.exe" in files:
                            cl_candidates.append(os.path.join(root, "cl.exe"))
                    
                    if cl_candidates:
                        print("\nFound cl.exe in Visual Studio directories:")
                        for candidate in cl_candidates:
                            print(f"  {candidate}")
                        print("\nYou need to set up the Visual Studio environment before using cl.exe.")
                        print("Run the Developer Command Prompt for Visual Studio or use VsDevCmd.bat")
    except Exception as e:
        print(f"Error checking for C++ compiler: {e}")
    
    print("\n===== Recommendations =====")
    print("1. To set up the Visual Studio environment:")
    print("   - Search for 'Developer Command Prompt for VS' in the Start menu")
    print("   - Or run the appropriate VsDevCmd.bat file")
    print("2. After setting up the environment, run 'nmake' to verify it's available")
    print("3. Then try compiling pgvector with the compile_pgvector.cmd script")
    
    return True

if __name__ == "__main__":
    check_vs_installation()
    print()
    input("Press Enter to exit...") 