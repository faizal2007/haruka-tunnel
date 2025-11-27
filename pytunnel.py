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
    """Main entry point - exit with proper codes for systemd."""
    try:
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        haruka = Haruka()
        
        # Read port mappings from database
        configs = haruka.list_port_configs()
        
        if not configs:
            print("✗ No port configurations found in database.")
            print("  Please use pymanage.py to create port configurations first.")
            return 1  # Return error code
        
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
            return 1  # Return error code
        
        # Pre-check: Detect and clean zombie ports before starting
        print("\n🔍 Checking for existing port bindings...\n")
        zombie_ports_cleaned = 0
        ports_already_active = []
        
        for config in configs:
            bind_port = config['server_bind_port']
            config_name = config['name']
            
            # Check if port is already bound on SSH server
            port_health = haruka.check_port_health_ssh_server(bind_port)
            
            if port_health:
                # Port is already bound - might be active tunnel or zombie
                print(f"  ⚠ Port {bind_port} [{config_name}] already in use on SSH server")
                
                # Try to determine if tunnel is working or zombie
                # If we can't connect to it, it's likely a zombie
                try:
                    # Give zombie port cleanup a chance
                    print(f"    → Attempting to cleanup stale binding...")
                    cleanup_success = haruka.kill_zombie_port_ssh_server(bind_port)
                    if cleanup_success:
                        print(f"    ✓ Cleaned up zombie port {bind_port}")
                        zombie_ports_cleaned += 1
                    else:
                        # Port might be active - will be overridden anyway
                        ports_already_active.append((config_name, bind_port))
                        print(f"    ⚠ Port {bind_port} appears to be in use (may be active tunnel)")
                except Exception as e:
                    print(f"    ℹ Could not cleanup port {bind_port}: {e}")
            else:
                print(f"  ✓ Port {bind_port} [{config_name}] - available")
        
        if zombie_ports_cleaned > 0:
            print(f"\n✓ Cleaned up {zombie_ports_cleaned} zombie port(s)")
            print("  Waiting 2 seconds for port release...\n")
            time.sleep(2)  # Wait for port to be released
        
        if ports_already_active:
            print(f"\n⚠ {len(ports_already_active)} port(s) already in use (will be rebound):")
            for config_name, port in ports_already_active:
                print(f"  • {config_name}: {port}")
            print()
        
        # Start all tunnels with a single SSH connection
        print("🚀 Starting tunnels...\n")
        tunnel = haruka.reverse_forward_multiple(port_mappings, background=True)
        
        if not tunnel:
            print("✗ Failed to start reverse port forwarding tunnels.")
            return 1  # Return error code
        
        # Show config details for each tunnel
        print("📊 Tunnel Status:\n")
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
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            return 0  # Return success code
            
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 2  # Return error code for unexpected errors
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
    exit_code = main()
    sys.exit(exit_code if exit_code is not None else 0)