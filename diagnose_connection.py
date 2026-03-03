import socket
import sys
import subprocess

print("=" * 60)
print("Supabase Connection Diagnostics")
print("=" * 60)
print()

# Test 1: Internet connectivity
print("Test 1: Internet Connectivity")
print("-" * 60)
test_hosts = [
    ('google.com', 'Google'),
    ('supabase.com', 'Supabase Main'),
    ('db.mxnpfsiyaqqwdcokukij.supabase.co', 'Your Supabase DB'),
]

internet_ok = False
for host, name in test_hosts:
    try:
        ip = socket.gethostbyname(host)
        print(f"[OK] {name:20} ({host})")
        print(f"     Resolved to: {ip}")
        if 'google' in host:
            internet_ok = True
    except socket.gaierror as e:
        print(f"[FAIL] {name:20} ({host})")
        print(f"       DNS Error: {e}")
print()

if not internet_ok:
    print("[ERROR] No internet connection detected!")
    print()
    print("Solutions:")
    print("1. Check your network connection")
    print("2. Check if you're behind a proxy")
    print("3. Try using a VPN")
    print()
    sys.exit(1)

# Test 2: Ping Supabase
print("Test 2: Network Reachability")
print("-" * 60)
try:
    result = subprocess.run(
        ['ping', '-n', '2', 'db.mxnpfsiyaqqwdcokukij.supabase.co'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("[OK] Can ping Supabase")
    else:
        print("[FAIL] Cannot ping Supabase (may be blocked)")
        print("       This is often normal - Supabase may block ICMP")
except Exception as e:
    print(f"[FAIL] Ping failed: {e}")
print()

# Test 3: DNS details
print("Test 3: DNS Resolution Details")
print("-" * 60)
try:
    result = subprocess.run(
        ['nslookup', 'db.mxnpfsiyaqqwdcokukij.supabase.co'],
        capture_output=True,
        text=True,
        timeout=10
    )
    print(result.stdout)
except Exception as e:
    print(f"[FAIL] nslookup failed: {e}")
print()

# Test 4: Port connectivity
print("Test 4: PostgreSQL Port (5432) Connectivity")
print("-" * 60)
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    # Try to get IP first
    try:
        ip = socket.gethostbyname('db.mxnpfsiyaqqwdcokukij.supabase.co')
        result = sock.connect_ex((ip, 5432))
        if result == 0:
            print(f"[OK] Port 5432 is open on {ip}")
        else:
            print(f"[FAIL] Port 5432 is closed or filtered on {ip}")
    except socket.gaierror:
        print("[FAIL] Cannot resolve hostname for port test")
    
    sock.close()
except Exception as e:
    print(f"[FAIL] Port test failed: {e}")
print()

# Test 5: Alternative connection methods
print("Test 5: Alternative Supabase Endpoints")
print("-" * 60)
alt_hosts = [
    ('mxnpfsiyaqqwdcokukij.supabase.co', 6543, 'Connection Pooler'),
    ('aws-0-ap-southeast-1.pooler.supabase.com', 5432, 'Regional Pooler'),
]

for host, port, name in alt_hosts:
    try:
        ip = socket.gethostbyname(host)
        print(f"[OK] {name:25} {host}")
        print(f"     IP: {ip}")
    except socket.gaierror:
        print(f"[FAIL] {name:25} {host}")
print()

# Summary
print("=" * 60)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 60)
print()
print("If DNS is failing:")
print("1. Check firewall/antivirus settings")
print("2. Try using Google DNS (8.8.8.8) or Cloudflare DNS (1.1.1.1)")
print("3. Flush DNS cache: ipconfig /flushdns")
print("4. Check if behind corporate proxy/firewall")
print()
print("Alternative approaches:")
print("1. Use Supabase web interface to import SQL")
print("2. Use Supabase API instead of direct PostgreSQL connection")
print("3. Contact Supabase support if project is inactive")
print()
print("Check Supabase project status:")
print("https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/general")

