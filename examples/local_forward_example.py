#!/usr/bin/env python3
"""
Example: Local Port Forwarding (Access Remote Services Locally)

This script creates a local tunnel to remote services by:
1. Listening on a local port (localhost:8080)
2. Forwarding connections through SSH tunnel
3. Connecting to a remote service (e.g., google.com:80)

Use case: You want to access a remote service locally, tunneled through your SSH server

This is DIFFERENT from reverse forwarding:
- Local forward: Your computer -> SSH Server -> Remote Service
- Reverse forward: Remote Service -> SSH Server -> Public Internet
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
    print("\nStopping port forwarding...")
    sys.exit(0)

def main():
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create test instance
    haruka = HarukaTest()

    print("Haruka Local Port Forwarding Example")
    print("====================================")
    print("\nThis exposes a REMOTE service locally through SSH tunnel")

    # Example: Forward local port 8080 to remote host google.com port 80
    # This will allow you to access google.com by going to http://localhost:8080
    local_port = 8080
    remote_host = "google.com"
    remote_port = 80

    print(f"Setting up local port forwarding:")
    print(f"  Local:  http://localhost:{local_port}")
    print(f"  Remote: {remote_host}:{remote_port}")
    print()
    print("Press Ctrl+C to stop forwarding")
    print()

    # Start forwarding in background
    success = haruka.forward_local_port(local_port, remote_host, remote_port, background=True)

    if success:
        print("Port forwarding is active!")
        print("Try opening http://localhost:8080 in your browser")
        print("Press Ctrl+C to stop...")

        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
    else:
        print("Failed to start port forwarding")

if __name__ == "__main__":
    main()