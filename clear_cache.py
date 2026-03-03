"""
Clear Python cache files to fix import issues
"""
import os
import shutil
import glob

def clear_pycache():
    """Remove all __pycache__ directories and .pyc files"""
    print("Clearing Python cache...")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            print(f"Removing: {cache_dir}")
            try:
                shutil.rmtree(cache_dir)
            except Exception as e:
                print(f"  Error removing {cache_dir}: {e}")
    
    # Remove .pyc files
    for pyc_file in glob.glob('**/*.pyc', recursive=True):
        print(f"Removing: {pyc_file}")
        try:
            os.remove(pyc_file)
        except Exception as e:
            print(f"  Error removing {pyc_file}: {e}")
    
    print("\nCache cleared!")

if __name__ == "__main__":
    clear_pycache()











