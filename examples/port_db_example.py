#!/usr/bin/env python3
"""
Example script demonstrating port forwarding database functionality.
"""

import sys
import os
# Import Haruka from parent package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from __init__ import Haruka

def main():
    haruka = Haruka()

    print("Haruka Port Forwarding Database Example")
    print("========================================")

    # Initialize the database
    print("\n1. Initializing database...")
    if not haruka.init_port_forwarding_db():
        print("Failed to initialize database")
        return

    # Add some example configurations
    print("\n2. Adding port configurations...")

    configs = [
        {
            "name": "web_server",
            "local_port": 8080,
            "remote_host": "example.com",
            "remote_port": 80,
            "server_bind_port": 8443,
            "description": "Forward local web traffic to remote web server"
        },
        {
            "name": "ssh_service",
            "local_port": 2222,
            "remote_host": "internal-server.local",
            "remote_port": 22,
            "server_bind_port": 22022,
            "description": "SSH access to internal server"
        },
        {
            "name": "database",
            "local_port": 5432,
            "remote_host": "db.internal",
            "remote_port": 5432,
            "server_bind_port": None,
            "description": "PostgreSQL database access"
        }
    ]

    for config in configs:
        success = haruka.add_port_config(**config)
        if not success:
            print(f"Failed to add {config['name']}")

    # List all configurations
    print("\n3. Listing all configurations:")
    all_configs = haruka.list_port_configs()

    print(f"Found {len(all_configs)} configuration(s):")
    for config in all_configs:
        bind_info = f" (server bind: {config['server_bind_port']})" if config['server_bind_port'] else ""
        print(f"  - {config['name']}: localhost:{config['local_port']} -> {config['remote_host']}:{config['remote_port']}{bind_info}")
        if config['description']:
            print(f"    Description: {config['description']}")

    # Demonstrate getting a specific config
    print("\n4. Getting specific configuration:")
    config = haruka.get_port_config("web_server")
    if config:
        print(f"Retrieved: {config['name']} - {config['description']}")
    else:
        print("Configuration not found")

    # Demonstrate deletion
    print("\n5. Deleting a configuration:")
    if haruka.delete_port_config("database"):
        print("Successfully deleted 'database' configuration")

    # Show remaining configurations
    print("\n6. Remaining configurations:")
    remaining = haruka.list_port_configs()
    for config in remaining:
        print(f"  - {config['name']}")

    print("\n✓ Port forwarding database example completed!")

if __name__ == "__main__":
    main()