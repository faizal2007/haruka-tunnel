#!/usr/bin/env python3
"""
Example: Reverse Port Forwarding (Expose Private Server to Public)

This script exposes your private servers to the public internet by:
1. Connecting to your public SSH server
2. Binding multiple ports on the SSH server to your local services
3. Public users can then access your private services via the SSH server's IP

Use cases:
- You have a web service on localhost:5000, want to expose it on server:5000
- You have a database on localhost:3000, want to expose it on server:8080
- You have multiple microservices and want to expose them simultaneously
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
    print("\nStopping reverse port forwarding...")
    sys.exit(0)

def single_port_example():
    """Example: Expose a single service"""
    print("=" * 70)
    print("EXAMPLE 1: Single Port Forwarding")
    print("=" * 70)
    
    haruka = Haruka()
    
    local_port = 5000          # Your private server's port
    bind_port = 5000           # Port to expose on SSH server

    print(f"\nConfiguration:")
    print(f"  Your private server:  localhost:{local_port}")
    print(f"  Public SSH server:    (configured in .env)")
    print(f"  Public access port:   {bind_port}")

    print(f"\n{'='*70}")
    print("Starting reverse port forwarding...")
    print("Press Ctrl+C to stop")
    print(f"{'='*70}\n")

    # Start reverse forwarding in background
    success = haruka.reverse_forward_tunnel(local_port, bind_port, background=True)

    if success:
        print("\n✓ Reverse port forwarding is active!")
        print(f"✓ Your private server on localhost:{local_port} is now publicly accessible")
        return True
    else:
        print("\n✗ Failed to start reverse port forwarding")
        return False

def multiple_ports_example():
    """Example: Expose multiple services simultaneously"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multiple Port Forwarding (SIMULTANEOUS)")
    print("=" * 70)
    
    haruka = Haruka()
    
    # Define multiple port mappings
    # Format: (local_port, bind_port)
    port_mappings = [
        (5000, 5000),   # Web service
        (22, 22025),   # SSH service
    ]

    print(f"\nConfiguration:")
    print(f"  Service 1: localhost:5000 -> server:5000 (Web)")
    print(f"  Service 2: localhost:3000 -> server:8080 (API)")
    print(f"  Service 3: localhost:8000 -> server:9000 (WebSocket)")

    print(f"\n{'='*70}")
    print("Starting multiple reverse port forwarding tunnels...")
    print("Press Ctrl+C to stop")
    print(f"{'='*70}\n")

    # Start all forwarding in background
    success = haruka.reverse_forward_multiple(port_mappings, background=True)

    if success:
        print("\n✓ All reverse port forwarding tunnels are active!")
        print(f"✓ Your services are now publicly accessible on multiple ports")
        return True
    else:
        print("\n✗ Failed to start multiple reverse port forwarding")
        return False

def dict_format_example():
    """Example: Using dictionary format for clearer configuration"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Multiple Ports with Dictionary Format (ALTERNATIVE)")
    print("=" * 70)
    
    haruka = Haruka()
    
    # Define port mappings using dictionaries (more readable)
    port_mappings = [
        {'local': 5000, 'bind': 5000},   # Web service
        {'local': 3000, 'bind': 8080},   # API service
        {'local': 8000, 'bind': 9000},   # WebSocket service
    ]

    print(f"\nConfiguration:")
    print(f"  Service 1: localhost:5000 -> server:5000 (Web)")
    print(f"  Service 2: localhost:3000 -> server:8080 (API)")
    print(f"  Service 3: localhost:8000 -> server:9000 (WebSocket)")

    print(f"\n{'='*70}")
    print("Starting multiple reverse port forwarding tunnels...")
    print("Press Ctrl+C to stop")
    print(f"{'='*70}\n")

    # Start all forwarding in background
    success = haruka.reverse_forward_multiple(port_mappings, background=True)

    if success:
        print("\n✓ All reverse port forwarding tunnels are active!")
        print(f"✓ Your services are now publicly accessible on multiple ports")
        return True
    else:
        print("\n✗ Failed to start multiple reverse port forwarding")
        return False

def main():
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Haruka Reverse Port Forwarding - Multiple Ports Example".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    print("\nThis script demonstrates three ways to expose multiple services:")
    print("  1. Single port (traditional method)")
    print("  2. Multiple ports using tuples (simultaneous)")
    print("  3. Multiple ports using dictionaries (alternative format)")

    print("\nChoose an example to run:")
    print("  [1] Single port forwarding")
    print("  [2] Multiple ports (simultaneous) - RECOMMENDED")
    print("  [3] Multiple ports (dictionary format)")
    print("  [4] Run all examples")
    
    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == "1":
        single_port_example()
    elif choice == "2":
        multiple_ports_example()
    elif choice == "3":
        dict_format_example()
    elif choice == "4":
        single_port_example()
        time.sleep(2)
        multiple_ports_example()
        time.sleep(2)
        dict_format_example()
    else:
        print("Invalid choice. Running multiple ports example (default)...")
        multiple_ports_example()

    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")

if __name__ == "__main__":
    main()