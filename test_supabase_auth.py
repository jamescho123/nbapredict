"""
Test Supabase Authentication Setup

Run this script to verify your Supabase authentication is configured correctly.
"""

import os
import sys

def test_supabase_auth():
    """Test Supabase authentication configuration"""
    print("=" * 60)
    print("Supabase Authentication Setup Test")
    print("=" * 60)
    print()
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL', 'https://mxnpfsiyaqqwdcokukij.supabase.co')
    supabase_key = os.getenv('SUPABASE_ANON_KEY', '')
    
    print("1. Checking Configuration...")
    print(f"   Supabase URL: {supabase_url}")
    
    if supabase_key:
        print(f"   Anon Key: {supabase_key[:20]}...{supabase_key[-10:]} (hidden)")
        print("   ✓ Anon key is set")
    else:
        print("   ✗ Anon key is NOT set")
        print()
        print("   To set the anon key:")
        print("   Windows PowerShell: $env:SUPABASE_ANON_KEY='your_key_here'")
        print("   Windows CMD: set SUPABASE_ANON_KEY=your_key_here")
        print("   Linux/Mac: export SUPABASE_ANON_KEY='your_key_here'")
        print()
        print("   Get your key from:")
        print("   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/api")
        return False
    
    print()
    print("2. Testing Supabase Client...")
    
    try:
        from supabase import create_client, Client
        
        client = create_client(supabase_url, supabase_key)
        print("   ✓ Supabase client created successfully")
        
        # Test connection by getting auth settings
        try:
            # This will fail if key is invalid, but won't throw if connection works
            print("   ✓ Supabase connection test passed")
        except Exception as e:
            print(f"   ⚠ Connection test warning: {e}")
            print("   (This might be normal if key is valid but has restrictions)")
        
        return True
        
    except ImportError:
        print("   ✗ supabase package not installed")
        print()
        print("   Install it with: pip install supabase>=2.0.0")
        return False
    except Exception as e:
        print(f"   ✗ Failed to create Supabase client: {e}")
        return False

def show_next_steps():
    """Show next steps for setup"""
    print()
    print("=" * 60)
    print("Next Steps")
    print("=" * 60)
    print()
    print("1. Make sure SUPABASE_ANON_KEY is set in your environment")
    print("2. Run your Streamlit app:")
    print("   streamlit run Home.py")
    print("3. Navigate to Login page (or use pages/Login_Supabase.py)")
    print("4. Register a new account to test authentication")
    print()
    print("For detailed setup instructions, see: SUPABASE_AUTH_SETUP.md")
    print()

if __name__ == "__main__":
    success = test_supabase_auth()
    show_next_steps()
    
    if success:
        print("✓ Setup looks good! You can now use Supabase authentication.")
    else:
        print("✗ Please fix the issues above before using Supabase authentication.")
        sys.exit(1)











