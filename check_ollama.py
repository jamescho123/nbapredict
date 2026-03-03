import requests
import socket
import json

def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def diagnose_ollama():
    print("--- Ollama Diagnostic Tool ---")
    
    # 1. Check Port Access (IPv4)
    print("\n1. Connectivity Check (127.0.0.1:11434):")
    if check_port('127.0.0.1', 11434):
        print("   [OK] Port 11434 is OPEN on 127.0.0.1")
    else:
        print("   [FAIL] Port 11434 is CLOSED on 127.0.0.1")

    print("\n2. Connectivity Check (localhost:11434):")
    if check_port('localhost', 11434):
        print("   [OK] Port 11434 is OPEN on localhost")
    else:
        print("   [FAIL] Port 11434 is CLOSED on localhost")

    # 2. Check API
    print("\n3. API Check (/api/tags):")
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"   [OK] API Accessible. Found {len(models)} models.")
            print("   Available Models:")
            for m in models:
                print(f"    - {m['name']}")
        else:
            print(f"   [FAIL] API returned error: {response.text}")
    except Exception as e:
        print(f"   [FAIL] API Connection Failed: {e}")

if __name__ == "__main__":
    diagnose_ollama()
