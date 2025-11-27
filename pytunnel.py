#!/usr/bin/env python

import warnings
import sys
import os
from __init__ import Haruka
import time
import signal
# Load the environment variables from the .env file
from dotenv import load_dotenv
load_dotenv()

def signal_handler(signum, frame):
    """Handle Ctrl+C to gracefully exit."""
    print("\nStopping reverse port forwarding...")
    sys.exit(0)
def main():
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    haruka = Haruka()
    
    # Read port mappings from database
    configs = haruka.list_port_configs()
    
    if not configs:
        print("✗ No port configurations found in database.")
        print("  Please use pymanage.py to create port configurations first.")
        return False
    
    print(f"\n📋 Found {len(configs)} port configuration(s) to forward:\n")
    
    # Get SSH_HOST from .env (this is where binding will happen)
    ssh_host_env = os.getenv('SSH_HOST')
    
    # Show all configs before starting
    for config in configs:
        public_ip = config.get('remote_host') or ssh_host_env
        print(f"  • {config['name']}: {config['local_port']} → {public_ip}:{config['server_bind_port']}")
    
    # Build port mappings for all configs (reuse single SSH connection)
    port_mappings = []
    config_names = {}  # Map (local_port, bind_port) to config name
    
    for config in configs:
        local_port = config['local_port']
        bind_port = config['server_bind_port']
        port_mappings.append((local_port, bind_port))
        config_names[(local_port, bind_port)] = config['name']
    
    # Test SSH connection first
    ssh_check = haruka.test_ssh_connection()
    
    if not ssh_check:
        print("✗ SSH connection test failed. Please check your SSH settings in the .env file.")
        return False
    
    # Start all tunnels with a single SSH connection
    print("\nStarting tunnels...\n")
    tunnel = haruka.reverse_forward_multiple(port_mappings, background=True)
    
    if not tunnel:
        print("✗ Failed to start reverse port forwarding tunnels.")
        return False
    
    # Show config details for each tunnel
    for config in configs:
        public_ip = config.get('remote_host') or ssh_host_env
        bind_port = config['server_bind_port']
        local_port = config['local_port']
        # Debug: print what we're getting from config
        if os.getenv('DEBUG') == 'True':
            print(f"DEBUG - config keys: {config.keys()}")
            print(f"DEBUG - remote_host: {config.get('remote_host')}, ssh_host_env: {ssh_host_env}")
        print(f"✓ [{config['name']}] Tunnel active: localhost:{local_port} → {public_ip}:{bind_port}")
    
    print(f"\n✓ Your private services are now publicly accessible")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    # # Start all forwarding in background
    # success = haruka.reverse_forward_multiple(port_mappings, background=True)
    # if success:
    #     print("\n✓ Reverse port forwarding is active!")
    #     print(f"✓ Your private services are now publicly accessible")
    #     return True
    # else:
    #     print("\n✗ Failed to start reverse port forwarding")
    #     return False
    
if __name__ == "__main__":
    main()