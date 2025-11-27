#!/usr/bin/env python3
"""
Test systemd compatibility of tunnel.sh wrapper script
"""
import os
import subprocess
import sys

def test_tunnel_sh_executable():
    """Test if tunnel.sh is executable"""
    if os.access('./tunnel.sh', os.X_OK):
        print("✅ tunnel.sh is executable")
        return True
    else:
        print("❌ tunnel.sh is not executable")
        return False

def test_tunnel_sh_shebang():
    """Test if tunnel.sh has correct shebang"""
    with open('./tunnel.sh', 'r') as f:
        first_line = f.readline()
    
    if first_line.startswith('#!/bin/bash'):
        print("✅ tunnel.sh has correct bash shebang")
        return True
    else:
        print(f"❌ tunnel.sh shebang is incorrect: {first_line}")
        return False

def test_tunnel_sh_syntax():
    """Test if tunnel.sh has valid bash syntax"""
    result = subprocess.run(['bash', '-n', './tunnel.sh'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ tunnel.sh has valid bash syntax")
        return True
    else:
        print(f"❌ tunnel.sh has syntax errors:\n{result.stderr}")
        return False

def test_env_file_exists():
    """Test if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file exists")
        return True
    else:
        print("❌ .env file not found")
        return False

def test_python_detection():
    """Test if tunnel.sh can detect Python"""
    result = subprocess.run(['bash', '-c', 'source .env 2>/dev/null; echo ${PYTHON_BIN:-venv/bin/python}'],
                          capture_output=True, text=True, cwd='.')
    python_bin = result.stdout.strip()
    print(f"ℹ️  Detected Python path: {python_bin}")
    
    if os.path.exists(python_bin):
        print(f"✅ Python binary exists at: {python_bin}")
        return True
    else:
        print(f"⚠️  Python binary not found at: {python_bin}")
        return False

def test_systemd_service_format():
    """Test if systemd service config is valid"""
    service_content = """[Unit]
Description=Haruka Tunnel - Reverse Port Forwarding Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/storage/linux/Projects/haruka-tunnel
ExecStart=/storage/linux/Projects/haruka-tunnel/tunnel.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=haruka-tunnel

[Install]
WantedBy=multi-user.target
"""
    
    # Basic validation
    required_sections = ['[Unit]', '[Service]', '[Install]']
    required_keys = {
        '[Unit]': ['Description'],
        '[Service]': ['Type', 'ExecStart', 'Restart'],
        '[Install]': ['WantedBy']
    }
    
    all_good = True
    for section in required_sections:
        if section not in service_content:
            print(f"❌ Missing section: {section}")
            all_good = False
    
    if all_good:
        print("✅ Systemd service file has valid structure")
        
        # Verify ExecStart uses tunnel.sh
        if 'ExecStart=/storage/linux/Projects/haruka-tunnel/tunnel.sh' in service_content:
            print("✅ ExecStart correctly points to tunnel.sh")
        else:
            print("❌ ExecStart does not point to tunnel.sh")
            all_good = False
    
    return all_good

def main():
    print("="*60)
    print("SYSTEMD COMPATIBILITY TEST FOR tunnel.sh")
    print("="*60 + "\n")
    
    tests = [
        ("Executable Check", test_tunnel_sh_executable),
        ("Shebang Check", test_tunnel_sh_shebang),
        ("Syntax Check", test_tunnel_sh_syntax),
        (".env File Check", test_env_file_exists),
        ("Python Detection", test_python_detection),
        ("Systemd Config", test_systemd_service_format),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 tunnel.sh is fully compatible with systemd!")
        print("\nYou can safely use it in systemd service with:")
        print("  ExecStart=/path/to/tunnel.sh")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
