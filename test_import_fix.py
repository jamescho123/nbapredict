"""
Test that nba_supabase_auth can be imported correctly
"""
import sys
import os

# Clear any cached imports
if 'nba_supabase_auth' in sys.modules:
    del sys.modules['nba_supabase_auth']
if 'supabase_auth' in sys.modules:
    del sys.modules['supabase_auth']

print("Testing import of nba_supabase_auth...")

try:
    from nba_supabase_auth import (
        init_auth_session, login_user, register_user, 
        check_authentication, logout_user, reset_password
    )
    print("✓ Successfully imported nba_supabase_auth")
    print("✓ All functions imported correctly")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure nba_supabase_auth.py exists in the current directory")
    print("2. Try deleting __pycache__ folders manually")
    print("3. Restart your Python interpreter/Streamlit app")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All imports working correctly!")











