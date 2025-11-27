#!/usr/bin/env python3
"""
PyManage Usage Examples

This script demonstrates various ways to use PyManage for managing
port forwarding configurations programmatically (non-interactive).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymanage import PyManage

def example_basic_workflow():
    """Example 1: Basic CRUD workflow."""
    print("\n" + "="*60)
    print("EXAMPLE 1: BASIC CRUD WORKFLOW")
    print("="*60)
    
    manager = PyManage()
    haruka = manager.haruka
    
    # Create
    print("\n1️⃣  Creating configurations...")
    haruka.add_port_config(
        name="api_server",
        local_port=8000,
        remote_host="localhost",
        remote_port=8000,
        server_bind_port=5000,
        description="REST API Server"
    )
    
    haruka.add_port_config(
        name="web_app",
        local_port=3000,
        remote_host="localhost",
        remote_port=3000,
        server_bind_port=5001,
        description="React Web App"
    )
    
    # List
    print("\n2️⃣  Listing all configurations...")
    configs = haruka.list_port_configs()
    print(f"   Total configurations: {len(configs)}")
    for config in configs:
        print(f"   - {config['name']}: {config['local_port']} -> {config['server_bind_port']}")
    
    # Read
    print("\n3️⃣  Reading specific configuration...")
    api_config = haruka.get_port_config("api_server")
    if api_config:
        print(f"   Found: {api_config['name']}")
        print(f"   Description: {api_config['description']}")
    
    # Delete
    print("\n4️⃣  Deleting a configuration...")
    haruka.delete_port_config("web_app")
    
    print("\n✓ Workflow complete!")

def example_port_health_monitoring():
    """Example 2: Port health monitoring."""
    print("\n" + "="*60)
    print("EXAMPLE 2: PORT HEALTH MONITORING")
    print("="*60)
    
    manager = PyManage()
    haruka = manager.haruka
    
    ports_to_check = [5000, 5001, 8000, 8001]
    
    print(f"\nChecking health of {len(ports_to_check)} ports...")
    
    results = []
    for port in ports_to_check:
        health = haruka.check_port_health_ssh_server(port)
        results.append(health)
        
        icon = "✓" if health['healthy'] else "✗"
        print(f"  {icon} Port {port}: {health['status']}")
    
    # Summary
    healthy = sum(1 for r in results if r['healthy'])
    zombie = sum(1 for r in results if r['status'] == 'zombie')
    
    print(f"\nSummary:")
    print(f"  Healthy: {healthy}")
    print(f"  Zombie: {zombie}")
    
    if zombie > 0:
        print(f"\n⚠️  Found {zombie} zombie binding(s)")
        print("   Consider running: pymanage.py -> Option 7 to kill them")

def example_auto_cleanup():
    """Example 3: Auto-cleanup before starting tunnel."""
    print("\n" + "="*60)
    print("EXAMPLE 3: AUTO-CLEANUP BEFORE TUNNEL")
    print("="*60)
    
    manager = PyManage()
    haruka = manager.haruka
    
    port = 5000
    
    print(f"\nScenario: Starting tunnel on port {port}")
    print("Workflow: Check → Cleanup if zombie → Start tunnel\n")
    
    # Step 1: Check
    print("1️⃣  Checking if port has zombie binding...")
    health = haruka.check_port_health_ssh_server(port)
    
    if health['status'] == 'zombie':
        print(f"   ⚠️  Found zombie binding on port {port}")
        
        # Step 2: Cleanup
        print("\n2️⃣  Cleaning up zombie port...")
        success = haruka.kill_zombie_port_ssh_server(port)
        
        if success:
            print(f"   ✓ Port {port} cleaned successfully")
        else:
            print(f"   ✗ Failed to clean port {port}")
            return
    else:
        print(f"   ✓ Port {port} is clean (status: {health['status']})")
    
    # Step 3: Ready to start
    print("\n3️⃣  Port is ready - can now start tunnel safely")
    print(f"   Command: haruka.reverse_forward_tunnel(3000, {port}, background=True)")

def example_batch_operations():
    """Example 4: Batch operations."""
    print("\n" + "="*60)
    print("EXAMPLE 4: BATCH OPERATIONS")
    print("="*60)
    
    manager = PyManage()
    haruka = manager.haruka
    
    # Create multiple configs
    print("\n1️⃣  Creating multiple configurations...")
    services = [
        ("service1", 3000, 5000, "Development service"),
        ("service2", 3001, 5001, "Staging service"),
        ("service3", 3002, 5002, "Production service"),
    ]
    
    for name, local, bind, desc in services:
        haruka.add_port_config(
            name=name,
            local_port=local,
            remote_host="localhost",
            remote_port=local,
            server_bind_port=bind,
            description=desc
        )
    
    print(f"   ✓ Created {len(services)} configurations")
    
    # List all
    print("\n2️⃣  Listing all configurations...")
    configs = haruka.list_port_configs()
    print(f"   Total: {len(configs)}\n")
    
    # Display in table format
    print("   Name           | Local | Bind | Description")
    print("   " + "-"*50)
    for config in configs:
        name = config['name'].ljust(14)
        local = str(config['local_port']).rjust(5)
        bind = str(config['server_bind_port']).rjust(4)
        desc = config['description'][:20]
        print(f"   {name} | {local} | {bind} | {desc}")
    
    # Cleanup
    print("\n3️⃣  Deleting all created configurations...")
    for config in configs:
        haruka.delete_port_config(config['id'])
    
    print("   ✓ All configurations deleted")

def example_test_connections():
    """Example 5: Test connections."""
    print("\n" + "="*60)
    print("EXAMPLE 5: TEST CONNECTIONS")
    print("="*60)
    
    manager = PyManage()
    haruka = manager.haruka
    
    print("\n1️⃣  Testing SSH connection...")
    ssh_ok = haruka.test_ssh_connection()
    
    if ssh_ok:
        print("   ✓ SSH connection successful")
    else:
        print("   ✗ SSH connection failed")
        print("   Check your .env configuration")
    
    print("\n2️⃣  Testing DuckDB...")
    db_ok = haruka.test_duckdb()
    
    if db_ok:
        print("   ✓ DuckDB operations successful")
    else:
        print("   ✗ DuckDB operations failed")

def main():
    """Run all examples."""
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  📚 PYMANAGE USAGE EXAMPLES  📚".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    examples = [
        ("Basic CRUD Workflow", example_basic_workflow),
        ("Port Health Monitoring", example_port_health_monitoring),
        ("Auto-Cleanup Before Tunnel", example_auto_cleanup),
        ("Batch Operations", example_batch_operations),
        ("Test Connections", example_test_connections),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    try:
        choice = input("\nSelect example (1-5) or 0 to run all: ").strip()
        
        if choice == '0':
            print("\nRunning all examples...\n")
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ Error in {name}: {e}")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                name, func = examples[idx]
                print(f"\nRunning: {name}\n")
                func()
            else:
                print("Invalid selection")
    
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n✓ Examples complete!\n")

if __name__ == "__main__":
    main()
