#!/usr/bin/env python3
"""
Example: Multiple Reverse Port Forwarding - Expose Multiple Services Simultaneously

This script exposes multiple private services to the public internet in parallel:
1. Each service runs on a different localhost port
2. Each is exposed on a different public port via SSH server
3. All connections happen simultaneously through a single SSH connection

Real-world scenario:
- Web UI on localhost:5000 exposed as server:5000
- REST API on localhost:3000 exposed as server:8080
- WebSocket server on localhost:8000 exposed as server:9000
- All running at the same time through one SSH tunnel
"""

import sys
import os
# Import Haruka from parent package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from __init__ import Haruka
import time
import signal

def signal_handler(signum, frame):
    """Handle Ctrl+C to gracefully exit."""
    print("\n\nStopping all reverse port forwarding tunnels...")
    sys.exit(0)

def main():
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Haruka: Multiple Services Exposed Simultaneously".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    # Create instance
    haruka = HarukaTest()

    # Multiple services configuration
    # You should have these services running on localhost before starting
    services = [
        {
            'name': 'Web UI',
            'local_port': 5000,
            'bind_port': 5000,
            'description': 'Main web interface'
        },
        {
            'name': 'SSH Server',
            'local_port': 22,
            'bind_port': 22222,
            'description': 'Secure shell access'
        },
    ]

    # Build port mappings
    port_mappings = [(s['local_port'], s['bind_port']) for s in services]

    print("\n📋 Services to Expose:")
    print("-" * 68)
    for i, service in enumerate(services, 1):
        print(f"  {i}. {service['name']}")
        print(f"     Local:  localhost:{service['local_port']}")
        print(f"     Public: server:{service['bind_port']}")
        print(f"     Info:   {service['description']}")
        print()

    print("⚠️  Prerequisites:")
    print("-" * 68)
    for service in services:
        print(f"  ✓ {service['name']} running on localhost:{service['local_port']}")
    print()

    print("🔄 Starting all tunnels simultaneously...")
    print("-" * 68)

    # Start all forwarding in background (simultaneous)
    success = haruka.reverse_forward_multiple(port_mappings, background=True)

    if success:
        print("\n" + "=" * 68)
        print("✅ SUCCESS: All reverse port forwarding tunnels are ACTIVE")
        print("=" * 68)
        
        print("\n📍 Your services are now publicly accessible:")
        for service in services:
            print(f"   • {service['name']:15} http://server:{service['bind_port']}")
        
        print("\n💡 How to test (from another machine):")
        print("   curl http://server:5000       # Test Web UI")
        print("   curl http://server:8080       # Test API")
        print("   # WebSocket typically tested via web browser or ws:// client")
        
        print("\n🛑 Press Ctrl+C to stop all tunnels")
        print("=" * 68 + "\n")

        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutdown initiated...")
    else:
        print("\n❌ FAILED: Could not start reverse port forwarding")
        print("   Check your SSH configuration and ensure services are running")
        sys.exit(1)

if __name__ == "__main__":
    main()
