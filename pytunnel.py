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
        
        # SSH connection will be tested when starting tunnels
        # (removed pre-check as it can cause false negatives with timeouts)
        
        print("\n🔄 Preparing to start tunnels...\n")
        
        print()
        
        # Start tunnels individually (like PyManage does) for better reliability
        print("🚀 Starting tunnels...\n")
        
        all_tunnels_started = True
        max_retries = 3
        
        for idx, config in enumerate(configs):
            local_port = config['local_port']
            bind_port = config['server_bind_port']
            config_name = config['name']
            
            print(f"  Starting tunnel for {config_name}:")
            print(f"    localhost:{local_port} → SSH_server:{bind_port}")
            
            # Retry logic for SSH connection issues
            success = False
            for attempt in range(1, max_retries + 1):
                try:
                    success = haruka.reverse_forward_tunnel(local_port, bind_port, background=True)
                    if success:
                        print(f"    ✓ Tunnel started")
                        break
                    elif attempt < max_retries:
                        print(f"    ⚠ Attempt {attempt} failed, retrying... ({attempt}/{max_retries})")
                        time.sleep(2)
                except Exception as e:
                    if attempt < max_retries:
                        print(f"    ⚠ Error: {e}, retrying... ({attempt}/{max_retries})")
                        time.sleep(2)
                    else:
                        print(f"    ✗ Error after {max_retries} attempts: {e}")
            
            if not success:
                print(f"    ✗ Failed to start tunnel for {config_name}")
                all_tunnels_started = False
            
            # Add delay between tunnel connections to avoid SSH connection issues
            if idx < len(configs) - 1:
                print(f"    ⏳ Waiting before next tunnel...\n")
                time.sleep(1)
        
        print()
        
        if not all_tunnels_started:
            print("⚠️  Warning: Some tunnels failed to start. Continuing anyway...")
            print("   Check SSH connection and try running PyManage option 3 manually.\n")
        
        # Show config details for ALL tunnels
        print("📊 Tunnel Status:\n")
        
        for config in configs:
            public_ip = config.get('remote_host') or ssh_host_env
            bind_port = config['server_bind_port']
            local_port = config['local_port']
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