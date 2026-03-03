import os
import subprocess
import tempfile
import sys
import time
import webbrowser

def download_vs_build_tools():
    """Download and install Visual Studio Build Tools with C++ workload"""
    print("===== Download and Install Visual Studio Build Tools =====")
    print()
    
    # Direct download link for VS Build Tools installer
    vs_build_tools_url = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
    
    # Create a temporary directory
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, "vs_BuildTools.exe")
    
    print(f"Downloading Visual Studio Build Tools installer to {installer_path}...")
    print("This may take a few minutes...")
    
    try:
        # Use PowerShell to download the file
        download_cmd = f'powershell -Command "& {{[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri \'{vs_build_tools_url}\' -OutFile \'{installer_path}\'}}"'
        subprocess.run(download_cmd, shell=True, check=True)
        print("Download complete!")
    except Exception as e:
        print(f"Error downloading installer: {e}")
        print("\nAlternative: Download manually from the following URL:")
        print("https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        webbrowser.open("https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        return False
    
    print("\nStarting Visual Studio Build Tools installer...")
    print("IMPORTANT: In the installer, make sure to select the following:")
    print("1. Select the 'Desktop development with C++' workload")
    print("2. In the right panel, ensure 'MSVC C++ x64/x86 build tools' is checked")
    print("3. Click 'Install' and wait for the installation to complete")
    print()
    print("After installation is complete, you'll need to restart your computer.")
    
    # Run the installer with the C++ workload
    try:
        install_cmd = f'"{installer_path}" --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive'
        print(f"Running: {install_cmd}")
        subprocess.Popen(install_cmd, shell=True)
    except Exception as e:
        print(f"Error starting installer: {e}")
        print(f"\nPlease run the installer manually: {installer_path}")
        return False
    
    print("\nThe installer has been launched.")
    print("Follow the instructions in the installer to complete the installation.")
    print("After installation is complete, restart your computer.")
    print("Then run check_vs_cpp.py again to verify the installation.")
    
    return True

if __name__ == "__main__":
    download_vs_build_tools()
    print()
    input("Press Enter to exit...") 