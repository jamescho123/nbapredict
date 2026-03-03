"""
Configure Supabase Authentication - Interactive Setup
"""

import os

SUPABASE_URL = 'https://mxnpfsiyaqqwdcokukij.supabase.co'
PROJECT_ID = 'mxnpfsiyaqqwdcokukij'

print("\n" + "="*70)
print("SUPABASE AUTHENTICATION CONFIGURATION")
print("="*70)

# Check current status
current_key = os.getenv('SUPABASE_ANON_KEY', '')
if current_key:
    print(f"\n[OK] SUPABASE_ANON_KEY is set (length: {len(current_key)} characters)")
    print("     Authentication should work!")
else:
    print("\n[WARNING] SUPABASE_ANON_KEY is NOT set")
    print("          This causes 'Supabase client not initialized' error")

# Check package
try:
    import supabase
    print("[OK] supabase package is installed")
except ImportError:
    print("[ERROR] supabase package is NOT installed")
    print("        Run: pip install supabase>=2.0.0")

print("\n" + "="*70)
print("TO FIX 'Supabase client not initialized' ERROR:")
print("="*70)
print("\n1. Get your Supabase Anon Key from:")
print(f"   https://supabase.com/dashboard/project/{PROJECT_ID}/settings/api")
print("\n2. Copy the 'anon' or 'public' key (long string)")
print("   WARNING: DO NOT use 'service_role' key")
print("\n3. Set environment variable:")
print("\n   PowerShell (temporary):")
print(f'   $env:SUPABASE_ANON_KEY="your_key_here"')
print("\n   PowerShell (permanent):")
print(f'   [System.Environment]::SetEnvironmentVariable("SUPABASE_ANON_KEY", "your_key_here", "User")')
print("\n   CMD:")
print(f'   set SUPABASE_ANON_KEY=your_key_here')
print("\n4. Restart your Streamlit app after setting")
print("\n" + "="*70)

